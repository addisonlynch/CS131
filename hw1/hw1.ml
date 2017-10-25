open List;;

let rec member x = function
| [] -> false
| hd::t -> hd = x || member x t;;

let rec subset a b = match a with
    [] -> true | h::t -> if List.exists (fun x -> x = h) b then subset t b else false;;

let equal_sets a b = subset a b && subset b a;;

let set_diff a b = List.filter (fun x -> not(List.mem x b)) a;;

let set_union a b = a @ b;;

let set_intersection a b = List.filter (fun x -> List.mem x b) a;;

let rec computed_fixed_point eq f x  = if (eq (f x) x) then x else (computed_fixed_point eq f (f x));;

let rec aux f p x = if p <= 0 then x else f (aux f (p-1) x);;

let rec computed_periodic_point eq f p x = if eq x (aux f p x) then x else computed_periodic_point eq f p (f x);;

let rec while_away s p x = if (p x) then x::(while_away s p (s x)) else [];;

let rec aux2 (a, b)=
match a with
0 -> []
| _ -> b::(aux2 ((a-1),b));;

let rec rle_decode lp = 
match lp with
h::t -> (aux2 h)@(rle_decode t)
| _ -> [];;


type ('nonterminal, 'terminal) symbol=
| N of 'nonterminal
| T of 'terminal

let equal_sets_wrapper a b c = equal_sets a c;;

let rec fixed_point_wrapper eq f x y =
if equal_sets_wrapper (f x y) x y then y else fixed_point_wrapper eq f x (f x y);;

let aux_symbol sym term=
match sym with
T s -> true
| N s -> mem s term;;

let rec aux_rule sym term =
match sym with
[] -> true
| beg::ende -> if aux_symbol beg term then aux_rule ende term
else false;;


let rec aux_arrange a b =
match a with
[] -> []
| s::t-> match s with 
_,p -> if aux_rule p b then [s]@aux_arrange t b
else aux_arrange t b;;


let rec aux_final a term =
match a with
[] -> term
| (lhs,rhs)::t-> if aux_rule rhs term then
if mem lhs term then aux_final t term
else aux_final t (lhs::term)
else aux_final t term;;


let filter_blind_alleys g = 
match g with
| (a, b) -> (a, aux_arrange b (fixed_point_wrapper equal_sets_wrapper aux_final b []));;
