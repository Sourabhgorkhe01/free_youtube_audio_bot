# Using YouTube Cookies with YouTube Audio Bot

## Why Cookies Are Needed

YouTube sometimes requires sign-in to confirm you are not a bot when downloading videos or audio. To bypass this, you need to export your YouTube cookies from your browser and provide them to the bot.

## How to Export YouTube Cookies

1. Open your browser (Chrome, Firefox, Edge, etc.) and go to [YouTube](https://www.youtube.com).
2. Log in to your YouTube account.
3. Use a browser extension to export cookies. Recommended extensions:
   - **EditThisCookie** (Chrome): https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
   - **Cookie Quick Manager** (Firefox): https://addons.mozilla.org/en-US/firefox/addon/cookie-quick-manager/
4. Export the cookies for the domain `youtube.com` and save them in the Netscape cookie file format.
5. Save the exported cookies file as `cookies.txt`.

## Where to Place the Cookies File

Place the `cookies.txt` file in the same directory as the bot's `downloader.py` file (usually the root of the `youtube_audio_bot` directory).

## Additional Resources

- [yt-dlp FAQ on passing cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- [Exporting YouTube cookies tips](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)

## Troubleshooting

- If you still get the "Sign in to confirm you’re not a bot" error, make sure your cookies file is up to date and correctly placed.
- Ensure you are logged in to YouTube in the browser from which you export cookies.
- If the bot does not detect the cookies file, it will attempt to download without it, which may cause errors.

## Contact

For further help, contact the bot developer or open an issue in the repository.
