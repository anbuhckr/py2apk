#! /usr/bin/env python3

import os, toml, jdk, zipfile, requests, platform, shutil
from string import Template
from PIL import Image
from tqdm import tqdm

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))
XML_FILE = os.path.join(PACKAGE_DIR, 'resources/AndroidManifest.xml')
ACTIVITY_FILE = os.path.join(PACKAGE_DIR, 'resources/activity_main.xml')
STRING_FILE = os.path.join(PACKAGE_DIR, 'resources/strings.xml')
STYLE_FILE = os.path.join(PACKAGE_DIR, 'resources/styles.xml')
HTML_FILE = os.path.join(PACKAGE_DIR, 'resources/index.html')
JAVA_FILE = os.path.join(PACKAGE_DIR, 'resources/MainActivity.java')
CLIENT_FILE = os.path.join(PACKAGE_DIR, 'resources/MyWebViewClient.java')
GRADLE_FILE = os.path.join(PACKAGE_DIR, 'resources/build.gradle')
ICON_FILE = os.path.join(PACKAGE_DIR, 'resources/icon.png')

class Py2Apk():

    def __init__(self) -> None:
        pass

    def render(self, source, destination, data):
        file_name = os.path.basename(source)
        with open(source, 'r') as template_file:
            t = Template(template_file.read()).substitute(data)
        if destination:
            if not os.path.exists(destination):
                os.makedirs(destination)       
            with open(os.path.join(destination, file_name), 'w') as destination_file:
                destination_file.write(t)
        else:
            with open(file_name, 'w') as destination_file:
                destination_file.write(t)

    def icons(self, data):        
        sizes = [{
            'name': 'mipmap-mdpi',
            'd': 48,
        }, {
            'name': 'mipmap-hdpi',
            'd': 72,
        }, {
            'name': 'mipmap-xhdpi',
            'd': 96,
        }, {
            'name': 'mipmap-xxhdpi',
            'd': 144,
        }, {
            'name': 'mipmap-xxxhdpi',
            'd': 192,
        }]
        im = Image.open(data)
        ext = data.split('.')[1]        
        im.save(f'src/main/ic_launcher-web.{ext}')
        for size in sizes:
            path = os.path.join('src', 'main', 'res', size['name'])
            if not os.path.exists(path):
                os.makedirs(path)
            im = Image.open(data)
            im.thumbnail((size['d'], size['d']))
            im.save(f'{path}/ic_launcher.{ext}')

    def unzip(self, source, destination):
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(destination)

    def download_file(self, name, url):
        response = requests.get(url, stream=True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f'download {name}')
        with open(name, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            os.remove(name)
            return self.download_data()        

    def install(self):
        print('download jdk...')
        if os.name == 'nt':
            jdk_11 = jdk.install('11')
            os.system(f"setx JAVA_HOME {jdk_11}")
            os.system(f"set JAVA_HOME={jdk_11)}")
        else:
            os.system(f"export JAVA_HOME={jdk_11}")
        print('jdk installed!')
        self.download_file('gradle.zip', 'https://services.gradle.org/distributions/gradle-7.1.1-bin.zip')
        self.unzip('gradle.zip', f'{os.path.expanduser("~")}/.py2apk/gradle')
        os.remove('gradle.zip')
        if os.name == 'nt':
            os.system(f'setx path "%PATH%;{os.path.expanduser("~")}\\.py2apk\\gradle\\gradle-7.1.1\\bin"')
            os.system(f'set path="%PATH%;{os.path.expanduser("~")}\\.py2apk\\gradle\\gradle-7.1.1\\bin"')        
        else:
            os.system(f'export PATH=$PATH:{os.path.expanduser("~")}/.py2apk/gradle/gradle-7.1.1/bin')            
        print('gradle installed!')
        if platform.system() == 'Windows':
            sdk = 'win'
        if platform.system() == 'Darwin':
            sdk = 'win'
        if platform.system() == 'Linux':
            sdk = 'win'
        self.download_file('cmdline-tools.zip', f'https://dl.google.com/android/repository/commandlinetools-{sdk}-7583922_latest.zip')
        self.unzip('cmdline-tools.zip', f'{os.path.expanduser("~")}/.py2apk/android-sdk/')
        os.remove('cmdline-tools.zip')
        shutil.move(f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/bin', f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/latest/bin')
        shutil.move(f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/lib', f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/latest/lib')
        shutil.move(f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/NOTICE.txt', f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/latest/NOTICE.txt')
        shutil.move(f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/source.properties', f'{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/latest/source.properties')
        if os.name == 'nt':
            os.system(f'setx ANDROID_HOME {os.path.expanduser("~")}\\.py2apk\\android-sdk')
            os.system(f'set ANDROID_HOME={os.path.expanduser("~")}\\.py2apk\\android-sdk')            
            os.system(f'setx path "%PATH%;{os.path.expanduser("~")}\\.py2apk\\android-sdk\\cmdline-tools\\latest\\bin')
            os.system(f'set path="%PATH%;{os.path.expanduser("~")}\\.py2apk\\android-sdk\\cmdline-tools\\latest\\bin')
            os.system(f'setx path "%PATH%;{os.path.expanduser("~")}\\.py2apk\\android-sdk\\emulator')
            os.system(f'set path="%PATH%;{os.path.expanduser("~")}\\.py2apk\\android-sdk\\emulator')
            os.system(f'setx path "%PATH%;{os.path.expanduser("~")}\\.py2apk\\android-sdk\\platform-tools')
            os.system(f'set path="%PATH%;{os.path.expanduser("~")}\\.py2apk\\android-sdk\\platform-tools')            
        else:
            os.system(f'export ANDROID_HOME={os.path.expanduser("~")}/.py2apk/android-sdk')
            os.system(f'export PATH=$PATH:{os.path.expanduser("~")}/.py2apk/android-sdk/cmdline-tools/latest/bin')
            os.system(f'export PATH=$PATH:{os.path.expanduser("~")}/.py2apk/android-sdk/emulator')
            os.system(f'export PATH=$PATH:{os.path.expanduser("~")}/.py2apk/android-sdk/platform-tools')
            os.system('exec bash')        
        os.system('sdkmanager --licenses')
        os.system('sdkmanager --install "system-images;android-30;google_apis;x86_64"')
        os.system('avdmanager create avd -n py2apk_emu -k "system-images;android-30;google_apis;x86_64"')
        os.system('adb start-server')
        print('android-sdk installed!')
        self.download_file('resources.zip', 'https://github.com/anbuhckr/py2apk/releases/download/v1.1.1/resources.zip')
        self.unzip('resources.zip', PACKAGE_DIR)
        os.remove('resources.zip')
        print('resources installed!')                  

    def new(self):
        data_toml = {'data': {
            'app_name': input('App name: '),            
            'package_name': input('Package name: '),            
            'version_name': input('Version: '),
            'status_color': input('Status bar color: ') or '#202225',
            'icon_file': input('Icon: ') or ICON_FILE,         
            'url_path': input('URL: ') or 'file:///android_asset/index.html',         
        }}
        with open('app.toml', 'w') as f:
            toml.dump(data_toml, f)
        data = data_toml['data']        
        self.render(XML_FILE, 'src/main/', data)
        self.render(ACTIVITY_FILE, 'src/main/res/layout/', data)
        self.render(STRING_FILE, 'src/main/res/values/', data)
        self.render(STYLE_FILE, 'src/main/res/values/', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/', data)
        data['host_name'] = '.'.join(reversed(data['package_name'].split('.')))
        self.render(CLIENT_FILE, f'{targetPath}/', data)
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, None, data)        
        self.render(HTML_FILE, 'src/main/assets/', data)
        self.icons(data['icon_file'])

    def build(self):
        data_toml = toml.load('app.toml')
        data = data_toml['data']        
        self.render(XML_FILE, 'src/main/', data)
        self.render(ACTIVITY_FILE, 'src/main/res/layout/', data)
        self.render(STRING_FILE, 'src/main/res/values/', data)
        self.render(STYLE_FILE, 'src/main/res/values/', data)
        dirs = data['package_name'].split('.')
        targetPath = os.path.join('src', 'main', 'java', *dirs)
        self.render(JAVA_FILE, f'{targetPath}/', data)
        data['host_name'] = '.'.join(reversed(data['package_name'].split('.')))
        self.render(CLIENT_FILE, f'{targetPath}/', data)
        data['version_code'] = data['version_name'].split('.')[0]        
        self.render(GRADLE_FILE, None, data)        
        self.icons(data['icon_file'])
        os.system('gradle wrapper')
        os.system('gradlew assembleDebug')

    def run(self):
        if os.name == 'nt':
            os.system('start /MIN emulator @py2apk_emu')
        else:
            os.system('emulator @py2apk_emu &')
        os.system('gradlew installDebug')

    def package(self):
        print('still on progress, manual package your apk with gradle')
        
