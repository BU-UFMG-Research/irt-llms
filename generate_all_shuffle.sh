for ((seed=0; seed<30; seed++))
do
    python3 generate_shuffle_exams.py --seed $seed
done