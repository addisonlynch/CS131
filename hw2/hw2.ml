let rec convert_rule rules nTerm  = 
	match rules with
	|[] -> []
	|(expr,rule)::t -> if nTerm = expr then rule::(convert_rule t nTerm)
						 else combine_rule t nTerm

let convert_grammar g =
	match g with
	|e,rules -> e, (convert_rule rules)


type ('nonterminal, 'terminal) symbol =
	| N of 'nonterminal
	| T of 'terminal



(*type:
'a * ('a -> ('a, 'b) symbol list list) ->
(('a * ('a, 'b) symbol list) list -> 'b list -> 'c option) ->
'b list -> 'c option = <fun>
*)

let parse_prefix gram accept frag =
	let rec matcher start rules_list rules_function derivation accept frag = 
		match rules_list with
		| [] -> None
		| h::t -> match match_one rules_function h accept (derivation@[(start, h)]) frag with
				  | None -> matcher start t rules_function derivation accept frag
			      | result -> result
	and match_one rules_function rule accept derivation frag =
		match rule with
		| [] -> accept derivation frag (*BASE CASE: return acceptor, derivation, and the fragment*)
		| sym::t -> match sym with (*For each symbol in the rule*)
			|(N nTerm) -> matcher nTerm (rules_function nTerm) rules_function derivation (match_one rules_function t accept) frag
				(*If the symbol is non-terminal, recurse back to matcher and continue*)
			|(T tTerm) -> match frag with
				|[] -> None
				|car::cdr -> if tTerm = car
					 then match_one rules_function t accept derivation cdr
					 else None in
				(*A terminal symbol triggers the base case. It recurses with an empty rule list, which ultimately will lead to the function returning the acceptor, derivation, and fragment*)
	matcher (fst gram) ((snd gram) (fst gram)) (snd gram) [] accept frag;; 
