let rec convert_rule rules nTerm  = 
	match rules with
	|[] -> []
	|(literal,rule)::t -> if nTerm = literal then rule::(convert_rule t nTerm)
						 else convert_rule t nTerm

let convert_grammar g =
	match g with
	|literal,rules -> literal, (convert_rule rules)


type ('nonterminal, 'terminal) symbol =
	| N of 'nonterminal
	| T of 'terminal



(*type:
'a * ('a -> ('a, 'b) symbol list list) ->
(('a * ('a, 'b) symbol list) list -> 'b list -> 'c option) ->
'b list -> 'c option = <fun>
*)

let parse_prefix gram accept frag =
	let rec matcher start rules_list func_param derivation accept frag = 
		match rules_list with
		| [] -> None (*If no prefix found, return none*)
		| h::t -> match match_one func_param h accept (derivation@[(start, h)]) frag with
				  (*Else, call the acceptor with derivation + suffix*)
				  | None -> matcher start t func_param derivation accept frag
				  (*If accepter returns none, go back one*)
			      | result -> result (*Else, return whatever the acceptor returns*)
	and match_one func_param rule accept derivation frag =
		match rule with
		| [] -> accept derivation frag (*BASE CASE: return acceptor, derivation, and the suffix*)
		| sym::t -> match sym with 
			|(N nTerm) -> matcher nTerm (func_param nTerm) func_param derivation (match_one func_param t accept) frag
				(*If the symbol is non-terminal, recurse back to matcher to find rules which match
				the current*)
			|(T tTerm) -> match frag with
				|[] -> None
				|car::cdr -> if tTerm = car
					 then match_one func_param t accept derivation cdr
					 else None in (*If the acceptor rejects, returns none*)
				(*A terminal symbol recurses in match_one and eventually
				triggers the base case when it recurses with an empty rule, 
				which ultimately will lead to the function returning the acceptor, 
				derivation, and suffix to the matcher, which will return the same.*)
	matcher (fst gram) ((snd gram) (fst gram)) (snd gram) [] accept frag;; 
