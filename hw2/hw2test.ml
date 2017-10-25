let accept_all derivation string = Some (derivation, string)
let accept_empty_suffix derivation = function
   | [] -> Some (derivation, [])
   | _ -> None


type phrase_heads_micro = 
  | S | DP | D | NP | VP | V 


let micro_grammar = 
  (S,
  function
    | S -> [[N DP; N VP]; [N DP; N VP]]
    | DP -> [[N D; N NP]; [N D; N NP]; [N D]]
    | D -> [[T"a"]; [T"the"]; [T"He"]]
    | NP -> [[T"man"]; [T"hole"]; [T"problem"]]
    | VP -> [[N V; N DP]; [N V; N DP]]
    | V -> [[T"filled"]; [T"fixed"]])

let test_2 = (parse_prefix micro_grammar accept_all 
                      ["He"; "fixed"; "the"; "problem"])
           = Some
           ([(S, [N DP; N VP;]); 
             (DP, [N D]); (D, [T"He"]);
             (VP, [N V; N DP]);
             (V, [T"fixed"]); (DP, [N D; N NP]);
             (D, [T"the"]); (NP, [T"problem"])], []) 


type phrase_heads_simple =
  | S | DP | D | NP | VP | V | PP | P


let simple_grammar = 
  (S,
  function
    | S -> [[N DP; N VP]; [N DP; N VP]]
    | DP -> [[N D; N NP; N PP]; [N D; N NP]; [N D]]
    | D -> [[T"a"]; [T"the"]; [T"I"]; [T"my"]]
    | NP -> [[T"food"]; [T"meal"]; [T"fingers"]; [T"fork"]; [T"plate"]]
    | VP -> [[N V; N DP]; [N V; N DP; N PP]]
    | V -> [[T"ate"]; [T"devoured"]; [T"munched"]]
    | PP -> [[N P; N DP]; [N P]]
    | P -> [[T"with"]; [T"using"]; [T"on"]])


let test_3 = (parse_prefix simple_grammar accept_all 
                      ["I"; "ate"; "the"; "food"; "with"; "my"; "fork"])
           = Some
           ([(S, [N DP; N VP;]); 
             (DP, [N D]); (D, [T"I"]);
             (VP, [N V; N DP]);
             (V, [T"ate"]); (DP, [N D; N NP; N PP]);
             (D, [T"the"]); (NP, [T"food"]); 
             (PP, [N P; N DP]);
             (P, [T"with"]); (DP, [N D; N NP]);
             (D, [T"my"]); (NP, [T"fork"])], [])




