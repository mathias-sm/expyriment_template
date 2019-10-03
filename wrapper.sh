#! /bin/bash
trap '{ rm -f $tempfile; }' EXIT

id=""
if [ $# -eq 0 ]
then
    id=$(dialog --output-fd 1 --inputbox "Input the unique ID of the participant" 8 60)
else
    id="$1"
fi

stop="0"
while [ $stop -eq 0 ]; do
    case $id in
        ''|*[!0-9]*)
            dialog --msgbox "Only numbers are allowed" 6 32
            id=$(dialog --output-fd 1 --inputbox "Input the unique ID of the participant" 8 60)
            stop="0" ;;
        *)
            stop="1" ;;
    esac
done

cmd_localizer='python3 localizer_standard.py
                --background-color 0 0 0 
                --text-color 250 250 250 --rsvp-display-time 250 
                --rsvp-display-isi 100 --picture-display-time 200 
                --picture-isi 0 --fs_delay_time 100 
                --stim-dir stim_files --total-duration 301000'


fpstat="stim/passive-static_$id.counter"
fpseq="stim/passive-seq_$id.counter"
foddity="stim/oddity_$id.counter"
floc="stim/oddity_$id.counter"
touch "$fpstat"
touch "$fpseq"
touch "$foddity"
touch "$floc"
cur_passive_static=$(cat $fpstat)
cur_passive_seq=$(cat $fpseq)
cur_loc=$(cat $floc)
cur_oddity=$(cat $foddity)
if [ -z "$cur_passive_static" ]; then
    cur_passive_static=0
    echo 0 > "$fpstat"
fi
if [ -z "$cur_passive_seq" ]; then
    cur_passive_seq=0
    echo 0 > "$fpseq"
fi
if [ -z "$cur_loc" ]; then
    cur_loc=0
    echo 0 > "$floc"
fi
if [ -z "$cur_oddity" ]; then
    cur_oddity=0
    echo 0 > "$foddity"
fi

resp=""

until [ "$resp" = "Quit" ]
do
    resp=$(dialog --clear --title "Experiment launcher for $id" \
                  --nocancel \
                  --output-fd 1 \
                  --menu "Select and press enter" \
                  24 50 20 \
                  P1 "Localizer Standard (Pinel)" \
                  P2 "Localizer Standard no_audio (Pinel)" \
                  P3 "Localizer Standard no_audio doubled (Pinel)" \
                  LNEW "Localizer Categories: new run" \
                  LREP "Localizer Categories: repeat last" \
                  1 "Passive Static: new run" \
                  2 "Passive Static: repeat last" \
                  3 "Passive Seq: new run" \
                  4 "Passive Seq: repeat last" \
                  5 "Oddity: new run" \
                  6 "Oddity: repeat last" \
                  Quit  "Quit")

    case $resp in
        P1)
          $cmd_localizer \
                    --subject-id "$id" \
                    --csv_file stim/session1_localizer_standard.csv;;
        P2)
          $cmd_localizer \
                    --subject-id "$id" \
                    --csv_file stim/session1_localizer_standard_noaudio.csv;;
        P3)
          $cmd_localizer \
                    --subject-id "$id" \
                    --csv_file stim/session1_localizer_standard_noaudio_doubled.csv;;
        LNEW)
            cur_loc=$((cur_loc + 1))
            python3 generate-geom-loc.py "$id" "$cur_passive_static"
            echo "$cur_loc" > "$floc"
            python3 launcher.py \
                    --subject-id "$id" \
                    "stim/geom-loc_${id}_${cur_passive_static}.csv" ;;
        LREP)
            if [ "$cur_loc" -eq "0" ]; then
                dialog --msgbox "No previous run to start again?" 6 32
            else
                python3 launcher.py \
                        --subject-id "$id" \
                        "stim/geom-loc_${id}_${cur_passive_seq}.csv"
            fi;;
        1)
            cur_passive_static=$((cur_passive_static + 1))
            python3 generate-passive-static.py "$id" "$cur_passive_static"
            echo "$cur_passive_static" > "$fpstat"
            python3 launcher.py \
                    --subject-id "$id" \
                    "stim/passive-static_${id}_${cur_passive_static}.csv" ;;
        2)
            if [ "$cur_passive_static" -eq "0" ]; then
                dialog --msgbox "No previous run to start again?" 6 32
            else
                python3 launcher.py \
                        --subject-id "$id" \
                        "stim/passive-static_${id}_${cur_passive_static}.csv"
            fi;;
        3)
            cur_passive_seq=$((cur_passive_seq + 1))
            python3 generate-passive-seq.py "$id" "$cur_passive_seq"
            echo "$cur_passive_seq" > "$fpseq"
            python3 launcher.py \
                    --subject-id "$id" \
                    "stim/passive-seq_${id}_${cur_passive_seq}.csv" ;;
        4)
            if [ "$cur_passive_seq" -eq "0" ]; then
                dialog --msgbox "No previous run to start again?" 6 32
            else
                python3 launcher.py \
                        --subject-id "$id" \
                        "stim/passive-seq_${id}_${cur_passive_seq}.csv"
            fi;;
        5)
            cur_oddity=$((cur_oddity + 1))
            python3 generate-oddity.py "$id" "$cur_oddity"
            echo "$cur_passive_seq" > "$foddity"
            python3 launcher.py \
                    --subject-id "$id" \
                    "stim/oddity_${id}_${cur_oddity}.csv" ;;
        6)
            if [ "$cur_oddity" -eq "0" ]; then
                dialog --msgbox "No previous run to start again?" 6 32
            else
                python3 launcher.py \
                        --subject-id "$id" \
                        "stim/oddity_${id}_${cur_oddity}.csv"
            fi;;
        7)
            echo "session 3";;
        Quit)
            true;;
        *)
            dialog --msgbox "I do not understand..." 6 32 ;;
    esac

done
