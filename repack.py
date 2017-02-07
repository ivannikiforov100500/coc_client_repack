from __future__ import print_function

import os
import sys
import shutil
from xml.etree import ElementTree

COC_APK_PATH = "F:/CoC/old/com.supercell.clashofclans-8-709-16.apk"
APKTOOL_PATH = "F:/CoC/apktool/apktool.jar"
JDK_BIN_PATH = "C:/Program Files (x86)/Java/jdk1.8.0_111/bin"
ANDROID_SDK_PATH = "C:/Users/Ruslan/AppData/Local/Android/sdk/build-tools/23.0.3"

KEY_STORE = "appkey.keystore"
KEY_STOREPASS = "Gfhjkm123"
KEY_PASS = "Gfhjkm123"
KEY_ALIAS = "MyKey"

OLD_PUBLICKKEY = "4102C28189897A48CEDFA8C6E5378F55624F9E8408FA8A376643DBBCE715B21A".decode("hex")
NEW_PUBLICKKEY = "72F1A4A4C48E44DA0C42310F800E96624E6DC6A641A9D41C3B5039D8DFADC27E".decode("hex")
OLD_HOST = b"gamea.clashofclans.com"
NEW_HOST = b"localhost".ljust(len(OLD_HOST), "\x00") #we assume that an old hostname is longer than a new

def applyPatch(file):
    f = open(file, "r+b")
    s = str(f.read())
    f.seek(0, 0)
    s = s.replace(OLD_PUBLICKKEY, NEW_PUBLICKKEY)
    s = s.replace(OLD_HOST, NEW_HOST)
    f.write(s)
    f.close()

def modifyBinaries(dir):
    for d in next(os.walk(dir + "/lib"))[1]:
        print("Patching {}".format("lib/" + d + "/libg.so"))
        #"".decode("hex")
        applyPatch(dir + "/lib/" + d + "/libg.so")


def modifyManifest(dir):
    file = dir + "/AndroidManifest.xml"
    ElementTree.register_namespace("android", "http://schemas.android.com/apk/res/android")
    e = ElementTree.parse(file)
    r = e.getroot()
    r.set("package", r.get("package") + "_m")
    print("Package name was changed to {}".format(r.get("package")))
    a = r.findall('.//application')[0]
    a.set("android:debuggable", "true")
    e.write(file)

def modifyStrings(dir):
    file = dir + "/res/values/strings.xml"
    e = ElementTree.parse(file)
    r = e.getroot()
    s = r.findall('.//string[@name="app_name"]')[0]
    s.text += " (Mod)"
    print("Application name was changed to {}".format(s.text))
    e.write(file)

if __name__ == "__main__":
    os.environ['PATH'] += os.pathsep + JDK_BIN_PATH
    os.environ['PATH'] += os.pathsep + ANDROID_SDK_PATH

    outDir = os.path.splitext(os.path.basename(COC_APK_PATH))[0]
    try:
        shutil.rmtree(outDir)
    except OSError:
        pass

    print("Unpacking original apk {} to {}".format(COC_APK_PATH, outDir))
    os.system("java -jar {} -f d {} -o {}".format(APKTOOL_PATH, COC_APK_PATH, outDir))

    #sys.exit()

    print("Applying patches")
    modifyManifest(outDir)
    modifyStrings(outDir)
    modifyBinaries(outDir)

    apkFile = outDir + ".apk"
    print("Packing patched apk {}".format(apkFile))
    os.system("java -jar {} b {} -o {}".format(APKTOOL_PATH, outDir, apkFile))

    print("Signing patched apk {}".format(apkFile))
    os.system("jarsigner -verbose -keystore {} -storepass {} -keypass {} {} {}".
        format(KEY_STORE, KEY_STOREPASS, KEY_PASS, apkFile, KEY_ALIAS))

    apkFile2 = outDir + "_mod.apk"
    try:
        os.remove(apkFile2)
    except OSError:
        pass
    print("Aligning signed apk {}".format(apkFile2))
    os.system("zipalign -v 4 {} {}".format(apkFile, apkFile2))
    os.remove(apkFile)

    print("Modified file {}".format(apkFile2))
