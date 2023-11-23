#!/usr/bin/python
# -*- coding: utf-8 -*-

# Working demonstration of loading and saving data from/to device memory on Android
# in a Python/Kivy application. Tested on Android 6, 10, and 12 (Kivy 2.1.0).
# Credit: github.com/antorix

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from android.permissions import request_permissions, Permission
from androidstorage4kivy import SharedStorage, Chooser  # all the job is done via these two modules
import os
import shutil


class KivyLoadSave(App):
    
    def build(self):
        request_permissions([Permission.READ_EXTERNAL_STORAGE,
                             Permission.WRITE_EXTERNAL_STORAGE])  # get the permissions needed

        self.opened_file = None  # file path to load, None initially, changes later on
        
        self.box = BoxLayout(orientation="vertical")  # create our simple interface
        self.button1 = Button(text="Click here to LOAD any text file\nfrom your device memory",
                              halign="center", size_hint_y=.2)
        self.button1.bind(on_release=lambda x: Chooser(self.chooser_callback).choose_content("text/*"))
        self.box.add_widget(self.button1)
        self.input = TextInput(hint_text="You will see loaded text here. Or type your own text to save it.",
                               input_type="text", background_color="white", background_normal = "")
        self.box.add_widget(self.input)
        self.button2 = Button(text="Click here to SAVE the text above\nto your device Documents folder",
                              halign="center", size_hint_y=.2,)
        self.button2.bind(on_release=self.save_file)
        self.box.add_widget(self.button2)
        self.popup_size_hint = [.85, .55]
        self.text_size = (
            Window.size[0]*self.popup_size_hint[0] *.9,
            Window.size[1]*self.popup_size_hint[1] *.9
        )

        return self.box

    def chooser_callback(self, uri_list):
        """ Callback handling the chooser """
        try:
            for uri in uri_list:
                self.uri = uri  # just to keep this uri for reference

                # We obtain the file from the Android's "Shared storage", but we can't work with it directly.
                # We need to first copy it to our app's "Private storage." Then the path to the copied path
                # gets returned to our 'opened_file' variable:
                self.opened_file = SharedStorage().copy_from_shared(uri)

        except Exception as e:
            pass

    def on_resume(self):
        """ We load the file when the chooser closes and our app resumes from the paused mode """
        if self.opened_file is not None:
            with open(self.opened_file, "r") as file:  # now we can read the obtained path in a normal Python way
                self.input.text = str(file.read()).strip()

            Popup(  # informing user about what exactly happened
                title="Info",
                content=Label(
                    text=f"File with the URI:\n\n{self.uri}\n\ncopied to the private storage:\n\n{self.opened_file}\n\nand loaded from there.\n\nFind its content in the text field.",
                    text_size=self.text_size, valign="center"
                ),
                size_hint=self.popup_size_hint
            ).open()

            self.opened_file = None  # reverting file path back to None

    def save_file(self, instance):
        """ Save the content of the input field to device's Documents folder """
        filename = os.path.join(SharedStorage().get_cache_dir(),
                                "My text from KivyLoadSave.txt")  # forming the path of our new file

        with open(filename, "w") as file:  # now we create it in a normal way, but only in the private storage
            file.write(self.input.text.strip())

        SharedStorage().copy_to_shared(private_file=filename)  # but then we copy it to the shared storage

        Popup(
            title="Info",
            content=Label(
                text=f"File:\n\n{filename}\n\ncreated and copied to your Documents folder (because Android thinks it's a document), check it there!",
                text_size=self.text_size, valign="center"
            ),
            size_hint=self.popup_size_hint
        ).open()  # hurray!

        # Note that Android copies our file to the Documents folder. It was done automatically. Why?
        # Because we created a .txt file which Android recognizes as a document. If we create an .mp3 file,
        # it will go to the Music folder, etc. Let's try it:

        filename2 = os.path.join(SharedStorage().get_cache_dir(), "My audio track from KivyLoadSave.mp3")
        with open(filename2, "w") as file2:
            file2.write("")
        SharedStorage().copy_to_shared(private_file=filename2)

        # Check your Music folder now. Android also creates a subfolder named after your app.
        # This is the way Google now wants us to work with files and their "Collections".

        temp = SharedStorage().get_cache_dir()  # cleaning our file cache in the private storage
        if temp and os.path.exists(temp):
            shutil.rmtree(temp)


if __name__ == "__main__":
    KivyLoadSave().run()
