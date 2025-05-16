avconv -i $file -c:v libx264 -c:a libvorbis -sn

avconv -i ../recordings/13302_20131110190500.mpg -c:v libx264 -c:a libvorbis -sn -c:d copy -map 0 -map -0:3 -map -0:4 -map -0:5 -map -0:8  13302_20131110190500.mkv

sudo avconv -i Churchills\ größtes\ Spiel\ \(2012\).mkv -ss 00:10:27 -t 01:37:50 -c:v copy -c:a copy -map 0 Churchills\ größtes\ Spiel\ \(2012\)_new.mkv

# -sn --> no subtitle

-b 2000k -acodec libmp3lame -ac 2 -ar 44100 -ab 128k 
