# سلام روزګان راډیو — 90.2 FM

دا د Flask + SQLite پر بنسټ وېب‌سایټ دی. د خبرونو، عکسونو، غږیزو او ویډیویي فایلونو اپلوډ، د Admin پاسورډ، درې ژبې او ژوندی Player لري.

## په Windows 11 کې چلول

1. ZIP فایل Extract کړئ او فولډر په VS Code کې خلاص کړئ.
2. په همدې فولډر کې د `.env-password.txt` په نوم یو فایل جوړ کړئ؛ په لومړۍ کرښه کې **یو اوږد او ځانګړی پاسورډ (لږ تر لږه 12 توري)** ولیکئ. دا فایل له بل چا سره مه شریکوئ.
3. په `start_windows.bat` دوه ځله کلیک وکړئ. لومړی ځل انټرنېټ ته اړتیا لري، ځکه Flask او Waitress نصبوي.
4. کله چې سرور پیل شو، Chrome کې `http://127.0.0.1:5000` خلاص کړئ.
5. د مدیریت برخې ته لاړ شئ او په خپل پاسورډ ننوزئ. خبر، عکس، MP3، MP4 یا WebM فایل اپلوډ کړئ (هر فایل تر 25MB).
6. د ژوندۍ راډیو لپاره حقیقي HTTPS stream URL ورکړئ. 90.2 FM یوازې فریکونسي ده، نه آنلاین لینک.

**یادونه:** د لومړي ځل پاسورډ hash په `data/radio.sqlite3` کې خوندي کېږي؛ که وروسته `.env-password.txt` بدل کړئ، د پخواني اډمین پاسورډ ځای نه نیسي. د پاسورډ د بدلولو لپاره د اډمین مدیریت اضافي فیچر پکار دی.

## انلاین خپرول

دا پروژه یوازې په کمپیوټر کې تر چلېدو وروسته په اتومات ډول انلاین نه کېږي. د عامه وېب‌سایټ لپاره HTTPS ډومېن، د Python/WSGI هاستینګ، د `DATA_DIR` دایمي ذخیره، بیک اپ، HTTPS reverse proxy، او د اپلوډ فایلونو د malware scanning او اضافي rate limiting تدابیر اړین دي.

د Linux production سرور لپاره نمونه:

```bash
export ADMIN_PASSWORD='YOUR_UNIQUE_LONG_PASSWORD'
export SECRET_KEY='YOUR_RANDOM_64_CHARACTER_SECRET'
export COOKIE_SECURE=1
export DATA_DIR=/var/lib/salam-radio
waitress-serve --host=127.0.0.1 --port=8000 app:app
```

دا د HTTPS reverse proxy تر شا وکاروئ. د `DATA_DIR` ټول فولډر (SQLite او uploads) منظم بیک اپ کړئ. د پاسورډ فایل او data فولډر GitHub ته مه پورته کوئ. د راډیو اصلي سټریم لینک باید د سټریمینګ خدمت څخه واخلئ.

## محدودیتونه

- درې ژبې د وېب‌سایټ په مېنو او کنټرولونو کې فعالې دي؛ د خبرونو متن پخپله نه ژباړل کېږي.
- 3D ته ورته مایکروفون د CSS انیمېشن دی، حقیقي Three.js 3D ماډل نه دی.
- د عکس/ویډیو د لویو فایلونو لپاره cloud storage او CDN غوره دي.
- د انلاین production امنیت لپاره لا جلا security audit، login rate limiting، د پاسورډ بدلولو پروسه، HTTPS او operational monitoring ته اړتیا ده.
- `ADMIN_PASSWORD` یوازې د لومړي ځل database initialization لپاره کارېږي.
