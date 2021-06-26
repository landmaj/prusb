# PrUSB
-------
Wireless file upload for your 3D printer using Raspberry Pi Zero W.

Connect RPi to a USB port on your printer and upload files from a PC using a 
Samba share.

Why not OctoPrint? I already have one Raspberry Pi 4B running Home Assistant
gathering statistics from my printer over network (Prusa Connect). I do not
want to manage yet another program, and I do not mind a short walk to my printer
to hit a `print` button.

### Initial setup
1. Install DietPi on an SD card.
2. Configure WiFi before first boot (`dietpi-wifi.txt`).
3. Setup SSH for key-based authentication (`/home/dietpi/.ssh/authorized_keys`).
4. Disable root and password login in Dropbear (`/etc/default/dropbear`).
```
DROPBEAR_EXTRA_ARGS="-w -s"
```

### Enable mass storage
1. `/boot/config.txt` -> `dtoverlay=dwc2`
2. `/etc/modules` -> `dwc2`
3. Create an empty binary file. Change `count` to modify size (in MB):
```
sudo dd bs=1M if=/dev/zero of=/piusb.bin count=256
```
4. Format the file:
```
sudo mkdosfs /piusb.bin -F 32 -I
```
5. Create mount directory:
```
sudo mkdir /mnt/usb_share
```
6. Mount it automatically by adding it to `/etc/fstab`:
```
/piusb.bin /mnt/usb_share vfat users,umask=000 0 2
```
7. Reboot for the changes to take effect. 
8. Connect RPi to a computer and run this command to test if everything works:  
   **You may want to cut red wire in you USB cable to avoid powering RPi zero 
   from two sources at the same time and potential issues that may arise.**
```
sudo modprobe g_mass_storage file=/piusb.bin stall=0 ro=1
```

### Samba
1. Install Samba. Type `dietpi-software` and choose *Samba* as File Server 
   instead of the default `ProFTPD`.
2. You may want to change password: `smbpasswd -a dietpi`.
3. Change shared directory (either using the command below or manually 
   in `/etc/samba/smb.conf`):
```
sed -i '/path = /c\path = /mnt/usbshare' /etc/samba/smb.conf
```
4. Restart Samba:
```
sudo systemctl restart smbd.service
```
5. Everything done, you should now be able to access the share from another computer.


### Reconnect USB after uploading a file
1. Install Python 3 and pip using `dietpi-software`.
2. Install Watchdog:
```
sudo pip3 install watchdog
```
3. Install script which will automate reconnecting:
```
cd /usr/local/share
wget https://github.com/landmaj/prusb/raw/master/usbshare.py -O usb_share.py
```
4. Add service to start it automatically:

```
cd /etc/systemd/system
wget https://github.com/landmaj/prusb/raw/master/usbshare.service -O usbshare.service
sudo systemctl daemon-reload
sudo systemctl enable usbshare.service
sudo systemctl start usbshare.service
```


### Credits
[The MagPI Magazine](https://magpi.raspberrypi.org/articles/pi-zero-w-smart-usb-flash-drive)
[This StackExchange question](https://raspberrypi.stackexchange.com/questions/111878/pi-zero-with-g-mass-storage-configuration)
[DietPi forum](https://dietpi.com/phpbb/viewtopic.php?f=8&t=5&start=10#p56)
