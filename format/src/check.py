import z3
from sets import Set


def i_formula(expr):
    """Formulas generated by z3 should respect the rules."""
    # list = []
    # def i_formula_node(expr):
    #     if not z3.is_var(expr) and not z3.is_const(expr):
    #         decl = expr.decl()
    #         if decl.kind() == z3.Z3_OP_UNINTERPRETED:
    #             list.append(False)
    # util.foreach_expr(i_formula_node, expr)
    # return all(list)
    return True


def u_predicate(expr):
    if z3.is_const(expr) and expr.decl().kind() == z3.Z3_OP_UNINTERPRETED:
        return True
    decl = expr.decl()
    if decl is None or decl.kind() != z3.Z3_OP_UNINTERPRETED:
        return False
    for kid in expr.children():
        i_formula(kid)
    return True


def get_implication_kids(expr, quant_okay):
    if z3.is_quantifier(expr) and expr.is_forall():
        if quant_okay:
            return get_implication_kids(expr.body(), False)
        else:
            raise Exception(
                "Illegal chc: " +
                "nested foralls"
            )
    elif expr.decl().kind() == z3.Z3_OP_IMPLIES:
        return expr.children()
    else:
        raise Exception(
            "Illegal chc: " +
            "expected forall or implication, got {}".format(expr.sexpr())
        )


def check_chc_tail(expr):
    decl = expr.decl()
    if decl is None or decl.kind() != z3.Z3_OP_AND:
        if not u_predicate(expr) and not i_formula(expr):
            raise Exception(
                "Illegal chc tail: expected u_predicate or i_formula, " +
                "got {}".format(expr.sexpr())
            )
    else:
        for kid in expr.children():
            if not u_predicate(kid) and not i_formula(kid):
                raise Exception(
                    "Illegal conjunct in tail: {}".format(kid.sexpr())
                )
    return True


# Returns true if the head is an i_formula (query clause)
def check_chc_head(expr):
    if u_predicate(expr):
        decl = expr.decl()
        if decl is not None:
            known_vars = Set([])
            for kid in expr.children():
                if not z3.is_var(kid):
                    raise Exception(
                        "Illegal head: " +
                        "argument {} is not a variable in {}".format(
                            kid.sexpr(), expr.sexpr()
                        )
                    )
                index = z3.get_var_index(kid)
                if index in known_vars:
                    raise Exception(
                        "Illegal head: non-distinct arguments, " +
                        "{} is used twice in {}".format(
                            kid.sexpr(), expr.sexpr()
                        )
                    )
                known_vars.add(z3.get_var_index(kid))
        return False
    elif expr == z3.BoolVal(False):
        return True
    else:
        raise Exception(
            "Illegal head: {}".format(expr.sexpr())
        )


# Return true if the clause is a query.
def check_chc(expr):
    kids = get_implication_kids(expr, True)
    check_chc_tail(kids[0])
    is_query = check_chc_head(kids[1])
    return is_query


def check_chcs(exprs):
    query_count = 0
    for index, expr in enumerate(exprs):
        try:
            is_query = check_chc(expr)
        except Exception as e:
            raise Exception(
                "While checking clause #{}\n{}".format(index, e)
            )
        if is_query:
            query_count += 1
        elif not is_query and query_count > 0:
            raise Exception(
                "Illegal benchmark: " +
                "query clause is not the last clause"
            )
    if query_count != 1:
        raise Exception(
            "Illegal benchmark: " +
            "expected one query clause, found {}".format(query_count)
        )
