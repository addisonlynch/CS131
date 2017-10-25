let my_subset_test0 = subset [] []
let my_subset_test1 = subset [1;2;3] []
let my_subset_test2 = subset [1;3;1555] [1;3;4;5;6;7;2;232323;155;1355;1555]

let my_equal_sets_test0 = equal_sets [2;5] [2;5]
let my_equal_sets_test1 = equal_sets [3;4;6] [3;4;6]
let my_equal_sets_test2 = equal_sets [] []

let my_set_union_test0 = equal_sets (set_union [1;2;3] []) [1;2;3]
let my_set_union_test1 = equal_sets (set_union [3;6;2;1;5] [3]) [3;6;2;1;5]

let my_set_intersection_test0 = equal_sets (set_intersection [2;3;4] [1]) []
let my_set_intersection_test2 = equal_sets (set_intersection [] []) []													   

let my_set_diff_test0= equal_sets(set_diff [3;4;5;6;] [1;3;4;5;6;7;8;]) []
let my_set_diff_test1 = equal_sets(set_diff [] []) []

let my_computed_fixed_point_test0= computed_fixed_point (=) (fun x -> x / 2) 100000000 = 0


let my_computed_periodic_point_test0 = computed_periodic_point (=) (fun x -> -x) 2 1 = 1
let my_computed_periodic_point_test1 = computed_periodic_point (=) (fun x -> x/2) 0 (-1) = (-1)


let my_while_away_test0=
equal_sets(while_away ((+) 4) ((>) 10) 0) [0;4;8]

let my_while_away_test1=
equal_sets(while_away ((+) 2) ((>) 1) 0) [0]

let my_rle_decode_test0 = rle_decode [2,0;1,8] = [0;0;8]
let my_rle_decode_test1 = rle_decode [0,0;0,9] = []
let my_rle_decode_test2 = rle_decode [5,5;5,5] = [5;5;5;5;5;5;5;5;5;5;]


type nonterminals =
| L | M | N | O

let rules1 =
[L, [T "a"];
L, [T "c"; N M];
M, [T "d"];
N, [N O; T "b"];
O, [N N; T "a"]]

let grammar1 = L, rules1

let my_filter_blind_alleys_test0 = filter_blind_alleys grammar1 = (L, [L, [T"a"];
								    L, [T "c"; N M];
								    M, [T "d"]])





type awksub_nonterminals =
  | Expr | Lvalue | Incrop | Binop | Num

let awksub_rules =
   [Expr, [T"("; N Expr; T")"];
    Expr, [N Num];
    Expr, [N Expr; N Binop; N Expr];
    Expr, [N Lvalue];
    Expr, [N Incrop; N Lvalue];
    Expr, [N Lvalue; N Incrop];
    Lvalue, [T"$"; N Expr];
    Incrop, [T"++"];
    Incrop, [T"--"];
    Binop, [T"+"];
    Binop, [T"-"];
    Num, [T"0"];
    Num, [T"1"];
    Num, [T"2"];
    Num, [T"3"];
    Num, [T"4"];
    Num, [T"5"];
    Num, [T"6"];
    Num, [T"7"];
    Num, [T"8"];
    Num, [T"9"]]


type giant_nonterminals =
  | Conversation | Sentence | Grunt | Snore | Shout | Quiet

let giant_grammar =
  Conversation,
  [Snore, [T"ZZZ"];
   Quiet, [];
   Grunt, [T"khrgh"];
   Shout, [T"aooogah!"];
   Sentence, [N Quiet];
   Sentence, [N Grunt];
   Sentence, [N Shout];
   Conversation, [N Snore];
   Conversation, [N Sentence; T","; N Conversation]]

let giant_test0 =
  filter_blind_alleys giant_grammar = giant_grammar

let giant_test1 =
  filter_blind_alleys (Sentence, List.tl (snd giant_grammar)) =
    (Sentence,
     [Quiet, []; Grunt, [T "khrgh"]; Shout, [T "aooogah!"];
      Sentence, [N Quiet]; Sentence, [N Grunt]; Sentence, [N Shout]])

let giant_test2 =
  filter_blind_alleys (Sentence, List.tl (List.tl (snd giant_grammar))) =
    (Sentence,
     [Grunt, [T "khrgh"]; Shout, [T "aooogah!"];
      Sentence, [N Grunt]; Sentence, [N Shout]])

(* Grammar for testing filter_blind_alleys *)
