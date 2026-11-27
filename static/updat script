'use strict';

const $ = id => document.getElementById(id);

let lang = localStorage.getItem('srr_lang') || 'ps';
let posts = [];
let csrf = '';
let admin = false;
let stream = '';

// --- Weather, time and date strip (top of the site) ---
const TARINKOT = { lat: 32.62, lon: 65.87 };

function psTime(date) {
  try {
    return date.toLocaleTimeString('ps-AF', { timeZone: 'Asia/Kabul', hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch (e) {
    return date.toLocaleTimeString('en-GB', { timeZone: 'Asia/Kabul', hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
}

function psDate(date) {
  try {
    return date.toLocaleDateString('ps-AF', { timeZone: 'Asia/Kabul', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  } catch (e) {
    return date.toLocaleDateString('en-GB', { timeZone: 'Asia/Kabul', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  }
}

function tickClock() {
  const now = new Date();
  const clock = $('clock');
  if (clock) clock.textContent = psTime(now);
  const d = $('todayDate');
  if (d) d.textContent = psDate(now);
}

function weatherWord(code) {
  if (code === 0) return 'صاف';
  if (code <= 2) return 'لږ وریځ';
  if (code === 3) return 'وریځ';
  if (code === 45 || code === 48) return 'غبار';
  if (code >= 51 && code <= 57) return 'څاڅکی';
  if (code >= 61 && code <= 67) return 'باران';
  if (code >= 71 && code <= 77) return 'واوره';
  if (code >= 80 && code <= 82) return 'باران';
  if (code === 95) return 'تندر او باران';
  return '—';
}

async function loadWeather() {
  const w = $('weather');
  if (!w) return;
  try {
    const url = 'https://api.open-meteo.com/v1/forecast?latitude=' + TARINKOT.lat + '&longitude=' + TARINKOT.lon + '&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FKabul&forecast_days=1';
    const r = await fetch(url);
    if (!r.ok) throw new Error('weather');
    const j = await r.json();
    const c = j.current;
    const day = j.daily || {};
    const hi = day.temperature_2m_max ? day.temperature_2m_max[0] : null;
    const lo = day.temperature_2m_min ? day.temperature_2m_min[0] : null;
    let text = Math.round(c.temperature_2m) + '°C، ' + weatherWord(c.weather_code);
    if (hi !== null && lo !== null) text += ' (' + Math.round(lo) + '°–' + Math.round(hi) + '°)';
    w.textContent = text;
  } catch (e) {
    w.textContent = 'د هوا معلومات نشته';
  }
}

// --- Live player placeholder: a proper box until the Caster player appears ---
function watchCaster() {
  const box = $('playerBox');
  const text = $('playerBoxText');
  const retry = $('playerRetry');
  if (!box) return;
  let waited = 0;
  const timer = setInterval(() => {
    waited += 2;
    const frame = document.querySelector('.cstrEmbed iframe');
    if (frame) {
      box.hidden = true;
      clearInterval(timer);
      return;
    }
    if (waited >= 14) {
      clearInterval(timer);
      if (text) text.textContent = 'سټوډیو لا ژوندۍ نه ده — کله چې میکسر وصل شي او خپرونه ژوندۍ شي، پلیر به دلته ښکاره شي.';
      if (retry) retry.hidden = false;
    }
  }, 2000);
  if (retry) {
    retry.onclick = () => {
      retry.hidden = true;
      if (text) text.textContent = '⏳ ژوندۍ پلیر بارېږي…';
      const old = document.querySelector('script[src*="caster.fm/widgets/embed.js"]');
      if (old) old.remove();
      const s = document.createElement('script');
      s.src = 'https://cdn.cloud.caster.fm/widgets/embed.js';
      document.body.appendChild(s);
      watchCaster();
    };
  }
}

const dict = {
  ps: {
    brand: 'سلام روزګان راډیو',
    home: 'کورپاڼه',
    news: 'خبرونه',
    gallery: 'عکسونه',
    videos: 'ویډیوګانې',
    programs: 'خپرونې',
    admin: 'مدیریت',
    about: 'زموږ په اړه',
    backHome: 'بېرته کورپاڼې ته',
    tagline: 'ستاسې غږ، ستاسې راډیو',
    listen: 'ژوندۍ راډیو واورئ',
    latest: 'وروستي خبرونه',
    live: 'ژوندۍ راډیو',
    newsHint: 'د راډیو تازه خبرونه',
    addContent: 'نوی مطلب اضافه کړئ',
    type: 'ډول',
    title: 'عنوان',
    description: 'تشریح',
    imageUpload: 'فایل انتخاب کړئ',
    mediaUrl: 'د ویډیو یا غږ HTTPS لینک (اختیاري)',
    publish: 'خوندي کړئ',
    settings: 'د راډیو تنظیمات',
    streamUrl: 'د ژوندۍ راډیو HTTPS سټریم لینک',
    saveStream: 'سټریم خوندي کړئ',
    streamHint: 'FM فریکونسي په خپله انټرنېټي سټریم نه دی.',
    managePosts: 'خپل مطالب',
    export: 'JSON بیک اپ',
    footer: 'د سلام روزګان راډیو وېب‌سایټ',
    empty: 'تر اوسه مطالب نشته',
    delete: 'ړنګول',
    needStream: 'لومړی د مدیریت له لارې د راډیو سټریم لینک ولیکئ.',
    aboutTitle: 'د سلام روزګان راډیو په اړه',
    aboutIntro: 'سلام روزګان راډیو 90.2 FM د خپلو اورېدونکو لپاره د خبرونو، معلوماتو او بېلابېلو خپرونو رسنیز مرکز دی.',
    aboutMissionTitle: 'زموږ موخه',
    aboutMission: 'زموږ موخه د کره معلوماتو وړاندې کول، د ټولنې د غږ رسول او د پوهاوي پراخول دي.',
    aboutTeamTitle: 'زموږ ټیم',
    aboutContactTitle: 'اړیکه ونیسئ'
  },

  fa: {
    brand: 'رادیو سلام روزگان',
    home: 'صفحه اصلی',
    news: 'اخبار',
    gallery: 'عکس‌ها',
    videos: 'ویدیوها',
    programs: 'برنامه‌ها',
    admin: 'مدیریت',
    about: 'درباره ما',
    backHome: 'بازگشت به صفحه اصلی',
    tagline: 'صدای شما، رادیوی شما',
    listen: 'شنیدن رادیوی زنده',
    latest: 'آخرین اخبار',
    live: 'رادیوی زنده',
    newsHint: 'خبرهای تازه',
    addContent: 'افزودن مطلب',
    type: 'نوع',
    title: 'عنوان',
    description: 'توضیحات',
    imageUpload: 'انتخاب فایل',
    mediaUrl: 'لینک HTTPS رسانه (اختیاری)',
    publish: 'ذخیره',
    settings: 'تنظیمات رادیو',
    streamUrl: 'لینک HTTPS پخش زنده',
    saveStream: 'ذخیره لینک',
    streamHint: 'فرکانس FM به تنهایی پخش اینترنتی نیست.',
    managePosts: 'مطالب شما',
    export: 'پشتیبان JSON',
    footer: 'وب‌سایت رادیو سلام روزگان',
    empty: 'هنوز مطلبی نیست',
    delete: 'حذف',
    needStream: 'ابتدا لینک پخش زنده را در مدیریت وارد کنید.',
    aboutTitle: 'درباره رادیو سلام روزگان',
    aboutIntro: 'رادیو سلام روزگان 90.2 FM یک رسانه برای ارائه خبرها، اطلاعات و برنامه‌های گوناگون به شنوندگان است.',
    aboutMissionTitle: 'هدف ما',
    aboutMission: 'هدف ما ارائه اطلاعات دقیق، رساندن صدای جامعه و افزایش آگاهی عمومی است.',
    aboutTeamTitle: 'تیم ما',
    aboutContactTitle: 'تماس با ما'
  },

  en: {
    brand: 'Salam Rozgan Radio',
    home: 'Home',
    news: 'News',
    gallery: 'Photos',
    videos: 'Videos',
    programs: 'Programs',
    admin: 'Admin',
    about: 'About Us',
    backHome: 'Back to Home',
    tagline: 'Your voice, your radio',
    listen: 'Listen Live',
    latest: 'Latest News',
    live: 'Live Radio',
    newsHint: 'Latest news',
    addContent: 'Add content',
    type: 'Type',
    title: 'Title',
    description: 'Description',
    imageUpload: 'Choose file',
    mediaUrl: 'HTTPS media link (optional)',
    publish: 'Publish',
    settings: 'Radio settings',
    streamUrl: 'HTTPS live stream URL',
    saveStream: 'Save stream',
    streamHint: 'FM frequency alone is not an internet stream.',
    managePosts: 'Your posts',
    export: 'JSON backup',
    footer: 'Salam Rozgan Radio website',
    empty: 'No posts yet',
    delete: 'Delete',
    needStream: 'Set the live stream URL in Admin first.',
    aboutTitle: 'About Salam Rozgan Radio',
    aboutIntro: 'Salam Rozgan Radio 90.2 FM is a media platform providing news, information and a variety of programs for its listeners.',
    aboutMissionTitle: 'Our Mission',
    aboutMission: 'Our mission is to provide accurate information, amplify community voices and promote public awareness.',
    aboutTeamTitle: 'Our Team',
    aboutContactTitle: 'Contact Us'
  }
};

const t = key => (dict[lang] || dict.ps)[key] || key;

const el = (tag, cls, txt) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (txt !== undefined) n.textContent = txt;
  return n;
};

async function api(url, options = {}) {
  const r = await fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(csrf ? { 'X-CSRF-Token': csrf } : {})
    }
  });

  const v = await r.json();

  if (!r.ok) {
    throw Error(v.error || 'Request failed');
  }

  return v;
}

function setLanguage(selectedLanguage) {
  lang = dict[selectedLanguage] ? selectedLanguage : 'ps';

  localStorage.setItem('srr_lang', lang);

  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'en' ? 'ltr' : 'rtl';

  const languageSelect = $('language');

  if (languageSelect) {
    languageSelect.value = lang;
  }

  document.querySelectorAll('[data-i18n]').forEach(node => {
    const key = node.getAttribute('data-i18n');

    if (Object.prototype.hasOwnProperty.call(dict[lang], key)) {
      node.textContent = t(key);
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(node => {
    const key = node.getAttribute('data-i18n-placeholder');

    if (Object.prototype.hasOwnProperty.call(dict[lang], key)) {
      node.placeholder = t(key);
    }
  });

  document.querySelectorAll('[data-i18n-title]').forEach(node => {
    const key = node.getAttribute('data-i18n-title');

    if (Object.prototype.hasOwnProperty.call(dict[lang], key)) {
      node.title = t(key);
    }
  });

  render();

  document.dispatchEvent(
    new CustomEvent('srr:languagechange', {
      detail: { language: lang }
    })
  );
}

function render() {
  const sections = {
    news: 'newsList',
    photo: 'photoList',
    video: 'videoList',
    program: 'programList'
  };

  for (const [kind, id] of Object.entries(sections)) {
    const host = $(id);
    if (!host) continue;

    host.replaceChildren();

    const items = posts.filter(p => p.type === kind);

    if (!items.length) {
      host.append(el('div', 'empty', t('empty')));
    }

    for (const p of items) {
      const card = el('article', 'card post');

      if (
        p.image &&
        /\.(jpg|jpeg|png|webp|gif)(\?|$)/i.test(p.image)
      ) {
        const img = el('img');
        img.src = p.image;
        img.alt = p.title;
        img.loading = 'lazy';
        card.append(img);
      }

      const body = el('div', 'post-body');

      body.append(el('h3', '', p.title));

      if (p.description) {
        body.append(el('p', '', p.description));
      }

      const src = p.media || p.image;

      if (
        src &&
        (
          /\.(mp4|webm)(\?|$)/i.test(src) ||
          /\.(mp3|ogg|wav)(\?|$)/i.test(src)
        )
      ) {
        const isVideo = /\.(mp4|webm)(\?|$)/i.test(src);
        const media = el(isVideo ? 'video' : 'audio');

        media.src = src;
        media.controls = true;
        media.preload = 'none';

        body.append(media);
      }

      card.append(body);
      host.append(card);
    }
  }

  const list = $('adminList');

  if (!list) return;

  list.replaceChildren();

  if (admin) {
    for (const p of posts) {
      const row = el('div', 'admin-item');

      row.append(el('span', '', p.title));

      const button = el('button', '', t('delete'));
      button.type = 'button';

      button.onclick = async () => {
        if (!confirm('Delete / ړنګول؟')) return;

        try {
          await api(
            '/api/posts/' + encodeURIComponent(p.id),
            { method: 'DELETE' }
          );

          await refresh();
        } catch (error) {
          alert(error.message);
        }
      };

      row.append(button);
      list.append(row);
    }
  }
}

async function refresh() {
  posts = await api('/api/posts');
  render();
}

function adminView() {
  if ($('loginBox')) $('loginBox').hidden = admin;
  if ($('adminPanel')) $('adminPanel').hidden = !admin;
}

async function initialize() {
  const languageSelect = $('language');

  if (languageSelect) {
    languageSelect.addEventListener('change', event => {
      setLanguage(event.target.value);
    });
  }

  const loginBtn = $('loginBtn');

  if (loginBtn) {
    loginBtn.onclick = async () => {
      try {
        const result = await api('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            password: $('adminPassword').value
          })
        });

        csrf = result.csrf;
        admin = true;

        $('adminPassword').value = '';
        $('loginStatus').textContent = '';

        adminView();
        render();
      } catch (error) {
        $('loginStatus').textContent = error.message;
      }
    };
  }

  const logoutBtn = $('logoutBtn');

  if (logoutBtn) {
    logoutBtn.onclick = async () => {
      try {
        await api('/api/logout', { method: 'POST' });

        admin = false;
        csrf = '';

        adminView();
      } catch (error) {
        alert(error.message);
      }
    };
  }

  const postForm = $('postForm');

  if (postForm) {
    postForm.onsubmit = async event => {
      event.preventDefault();

      const data = new FormData();

      data.set('type', $('postType').value);
      data.set('title', $('postTitle').value.trim());
      data.set('description', $('postDescription').value.trim());
      data.set('media', $('postMedia').value.trim());

      if ($('postImage').files[0]) {
        data.set('image', $('postImage').files[0]);
      }

      try {
        await api('/api/posts', {
          method: 'POST',
          body: data
        });

        postForm.reset();

        $('formStatus').textContent = '✓ Saved / خوندي شو';

        await refresh();
      } catch (error) {
        $('formStatus').textContent = error.message;
      }
    };
  }

  const saveStream = $('saveStream');

  if (saveStream) {
    saveStream.onclick = async () => {
      try {
        const url = $('streamUrl').value.trim();

        await api('/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ stream: url })
        });

        stream = url;

        $('playerStatus').textContent = '✓ Saved';

        const radio = $('radio');

        if (radio) {
          radio.pause();
          radio.removeAttribute('src');
          radio.load();
        }
      } catch (error) {
        $('playerStatus').textContent = error.message;
      }
    };
  }

  const playBtn = $('playBtn');

  if (playBtn) {
    playBtn.onclick = async () => {
      const audio = $('radio');
      if (!audio) return;

      if (!audio.paused) {
        audio.pause();
        return;
      }

      if (!stream) {
$('playerStatus').textContent = 'د ژوندۍ راډیو د اورېدو لپاره لاندې Caster.fm پلیر وکاروئ.'; 
        return;
      }

      if (audio.src !== stream) {
        audio.src = stream;
      }

      try {
        await audio.play();
        $('playerStatus').textContent = '';
      } catch (error) {
        $('playerStatus').textContent =
          'Stream error: ' + error.message;
      }
    };
  }

  const volume = $('volume');
  const radio = $('radio');

  if (radio) {
    if (volume) {
      volume.oninput = event => {
        radio.volume = Number(event.target.value);
      };

      radio.volume = Number(volume.value);
    } else {
      radio.volume = 0.8;
    }

    radio.onplay = () => {
      if (playBtn) playBtn.textContent = '❚❚';

      const bars = document.querySelector('.bars');

      if (bars) bars.classList.add('playing');
    };

    radio.onpause = () => {
      if (playBtn) playBtn.textContent = '▶️';

      const bars = document.querySelector('.bars');

      if (bars) bars.classList.remove('playing');
    };

    radio.onerror = () => {
      if ($('playerStatus')) {
        $('playerStatus').textContent =
          'Unable to play stream. Check URL / format.';
      }
    };
  }

  const exportBtn = $('exportBtn');

  if (exportBtn) {
    exportBtn.onclick = () => {
      const blob = new Blob(
        [JSON.stringify({ posts, stream }, null, 2)],
        { type: 'application/json' }
      );

      const url = URL.createObjectURL(blob);
      const anchor = el('a');

      anchor.href = url;
      anchor.download = 'salam-rozgan-backup.json';
      anchor.click();

      setTimeout(() => URL.revokeObjectURL(url), 1000);
    };
  }

  if ($('year')) {
    $('year').textContent = new Date().getFullYear();
  }

  setLanguage(lang);

  tickClock();
  setInterval(tickClock, 1000);
  loadWeather();
  const wr = $('weatherRefresh');
  if (wr) wr.onclick = loadWeather;
  watchCaster();

  try {
    const state = await api('/api/status');

    admin = state.admin;
    csrf = state.csrf || '';

    adminView();

    const settings = await api('/api/settings');

    stream = settings.stream || '';

    if ($('streamUrl')) {
      $('streamUrl').value = stream;
    }

    await refresh();
  } catch (error) {
    if ($('playerStatus')) {
      $('playerStatus').textContent =
        'Connection error: ' + error.message;
    }
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}
