#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os  # file handling
import shutil  # file handling2
import zipfile  # zipping
import argparse  # arguments


# --------------------
# Printing functions and classes
# --------------------
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_bold(text):
    print(color.BOLD + text + color.END)


def print_info(build_infos, ipa_name):
    print('+------------------------------------------------------------------------------+')
    print('| IPA Analyzer - ' + ipa_name + '                                                                ')
    print('+------------------------------------------------------------------------------+')

    bundleId = build_infos.bundleId
    versionNum = build_infos.versionNumber
    buildNum = build_infos.buildNumber
    appIconName = build_infos.appIconName

    if appIconName == None:
        appIconName = "No app icon was found"

    print('Bundle Identifier: ' + bundleId)
    print('Version number: ' + versionNum)
    print('Build number: ' + buildNum)
    print('App icon name: ' + appIconName)

    print('+------------------------------------------------------------------------------+')


# --------------------
# Core iOS IPA classes
# --------------------

class IosBuildInfo:

    def __init__(self, bundleId, versionNumber, buildNumber, appIconName, bundleExecutable):
        self.bundleId = bundleId
        self.versionNumber = versionNumber
        self.buildNumber = buildNumber
        self.appIconName = appIconName
        self.bundleExecutable = bundleExecutable


class IosIpa:

    def __init__(self, ipa_path):

        self.path = ipa_path
        self.name = ipa_path.rsplit('/', 1)[1]

        self.tmp_dir = os.getcwd() + '/_tmp/ipa_' + self.name
        self.unzip()

        self.infoplist_filepath = self.get_info_plist()
        self.buildInfo = self.get_build_infos()
        self.iconsArray = self.get_icon_files()

    # Unzip IPA to TMP directory
    def unzip(self):
        zip_ref = zipfile.ZipFile(self.path, 'r')
        zip_ref.extractall(self.tmp_dir)
        zip_ref.close()

    # Delete TMP directory
    def delete_tmp(self):
        shutil.rmtree(os.getcwd() + '/_tmp/')

    def find_file_path(self, name):

        payload_dir = self.tmp_dir + '/Payload'

        # find file
        infoplist_filepath = None

        for app_file in os.listdir(payload_dir):
            if app_file.endswith('.app'):
                for app_subfile in os.listdir(payload_dir + '/' + app_file):
                    if app_subfile == name:
                        infoplist_filepath = payload_dir + '/' + app_file + '/' + app_subfile

        return infoplist_filepath

    # Get info plist filepath
    def get_info_plist(self):
        return self.find_file_path("Info.plist")

    def open_binary_file(self):
        print(self.buildInfo.bundleExecutable)
        bin_path = self.find_file_path(self.buildInfo.bundleExecutable)
        return open(bin_path, "rb")

    # Get build infos as IosBuildInfo object
    def get_build_infos(self):

        # Required params
        bundleIdString = None
        versionNumber = None
        buildNumber = None
        appIcon = None
        bundleExecutable = None

        # Get plist file
        plist_content = None
        with open(self.infoplist_filepath) as plist:
            plist_content = plist.readlines()

        # Find the required info
        index = 0
        for plist_line in plist_content:

            if "CFBundleIdentifier" in plist_line:
                bundleIdString = get_content_from_string_xml(plist_content[index + 1])

            if "CFBundleShortVersionString" in plist_line:
                versionNumber = get_content_from_string_xml(plist_content[index + 1])

            if "CFBundleVersion" in plist_line:
                buildNumber = get_content_from_string_xml(plist_content[index + 1])

            if "CFBundleIconFiles" in plist_line:
                appIcon = get_content_from_string_xml(plist_content[index + 2])

            if "CFBundleExecutable" in plist_line:
                bundleExecutable = get_content_from_string_xml(plist_content[index + 1])

            index = index + 1

        return IosBuildInfo(bundleIdString, versionNumber, buildNumber, appIcon, bundleExecutable)

    # Return an array of App icon file names
    def get_icon_files(self):

        payload_dir = self.tmp_dir + '/Payload'

        # find files
        icon_filepath_array = []

        if self.buildInfo.appIconName == None:
            return icon_filepath_array

        for app_file in os.listdir(payload_dir):
            if app_file.endswith('.app'):
                for app_subfile in os.listdir(payload_dir + '/' + app_file):
                    if app_subfile.startswith(self.buildInfo.appIconName):
                        appicon_filepath = payload_dir + '/' + app_file + '/' + app_subfile
                        icon_filepath_array.append(appicon_filepath)

        return icon_filepath_array


# --------------------
# Plist file parser extension
# --------------------

# Returning content form a <string>ABC</string> plist line
def get_content_from_string_xml(line):
    if 'string' in line:
        content = line.replace('<string>', '')
        content = content.replace('</string>', '')
        content = content.replace('\n', '')
        content = content.strip(' ')
        content = content.strip('\t')
        return content
    else:
        return None
