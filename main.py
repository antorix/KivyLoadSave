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
from android.permissions import request_permissions, Permission
from androidstorage4kivy import SharedStorage, Chooser
from kivy.clock import Clock
import os
import shutil


class KivyLoadSave(App):
    
    def build(self):
        request_permissions([Permission.READ_EXTERNAL_STORAGE,
                             Permission.WRITE_EXTERNAL_STORAGE])  # get the permissions needed
 
        self.chooser = Chooser(self.chooser_callback)  # standard Android dialog to browse files

        self.opened_file = None  # file path to load, None initially, changes later on
        
        self.box = BoxLayout(orientation="vertical")  # create our simple interface
        self.button1 = Button(text="Click here to LOAD any text file\nfrom your device memory",
                              halign="center", size_hint_y=.2)
        self.button1.bind(on_release=lambda x: self.chooser.choose_content("text/*"))
        self.box.add_widget(self.button1)
        self.input = TextInput(hint_text="You will see loaded text here. Or type your own text to save it.",
                               input_type="text", background_color="white", background_normal = "")
        self.box.add_widget(self.input)
        self.button2 = Button(text="Click here to SAVE the text above\nto your device Documents folder",
                              halign="center", size_hint_y=.2,)
        self.button2.bind(on_release=self.save_file)
        self.box.add_widget(self.button2)
        self.popup_size_hint = [.75, .25]

        return self.box

    def chooser_callback(self, uri_list):
        """ Callback handling the chooser """
        try:
            for uri in uri_list:
                # We obtain the file from the Android's "Shared storage", but we can't work with it directly.
                # We need to first copy it to our apps "Private storage." Then our 'opened_file' variable
                # receives the path of the copied file:
                self.opened_file = SharedStorage().copy_from_shared(uri)

            # The Clock approach below looks a bit crazy, but it's the way to invoke 'load_file'
            # outside of the callback (otherwise it won't work):
            Clock.schedule_interval(self.load_file, .05)

        except Exception as e:
            pass

    def load_file(self, *args):
        """ Loading the file and deciding what to do with it """
        if self.opened_file is not None:
            with open(self.opened_file, "r") as file:  # now we can read the obtained path in a normal Python way
                self.input.text = str(file.read()).strip()

            Popup(
                title="Info",
                content=Label(
                    text="Loaded successfully. Find\nthe content of the file in the\ntext field."
                ),
                size_hint=self.popup_size_hint
            ).open()

            self.opened_file = None  # reverting path back to None

        Clock.unschedule(self.load_file)  # stop scheduled action in the end

    def save_file(self, instance):
        """ Save the content of the self.input to device's Documents folder """
        filename = os.path.join(SharedStorage().get_cache_dir(),
                                "My text from KivyLoadSave.txt")  # forming the path of our new file

        with open(filename, "w") as file:  # now we can create it in a normal way, but only in the private storage
            file.write(self.input.text.strip())

        SharedStorage().copy_to_shared(private_file=filename)  # but then we can copy it to the shared storage

        Popup(
            title="Info",
            content=Label(
                text=f"File successfully saved to\nyour Documents, check it there!"
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

        # Check your Music folder now.

        temp = SharedStorage().get_cache_dir()  # clean our temporary file storage
        if temp and os.path.exists(temp):
            shutil.rmtree(temp)

        # Read https://github.com/Android-for-Python/androidstorage4kivy
        # for more technical details on this.


if __name__ == "__main__":
    KivyLoadSave().run()
