# FACEBOOK-PC-CLONE
PAID
WhatsApp : +8801317029056


(install all in your termux one by one.)

termux-change-repo
termux-setup-storage
pkg update -y && pkg upgrade -y
pkg install x11-repo -y
pkg install python git chromium chromedriver -y
ls /data/data/com.termux/files/usr/bin | grep chrom
ln -sf /data/data/com.termux/files/usr/bin/chromium-browser /data/data/com.termux/files/usr/bin/chromium
chromedriver --version
pip install selenium colorama requests
git clone https://github.com/ariyanahamed282/FACEBOOK-PC-CLONE.git
cd FACEBOOK-PC-CLONE
python main.py
