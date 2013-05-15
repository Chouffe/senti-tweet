rm classifiers/*
./train.py -p 200 -n 100 -e 100 -f classifiers/pos1.cl &
./train.py -p 200 -n 100 -e 100 -f classifiers/pos2.cl &
./train.py -p 100 -n 200 -e 100 -f classifiers/neg1.cl &
./train.py -p 100 -n 200 -e 100 -f classifiers/neg2.cl &
./train.py -p 100 -n 100 -e 200 -f classifiers/neut1.cl &
./train.py -p 100 -n 100 -e 200 -f classifiers/neut2.cl &
