'''
Module for model transformation operations.
'''

from models import Reaction, ConstraintBasedModel, GPRConstrainedModel

def make_irreversible(model):
    """ Splits all reversible reactions into forward and backward directions.
    
    Arguments:
        model : StoichiometricModel or any subclass
        
    Returns:
        dictionary : mapping olds ids to new ids
    """
    
    mapping = dict()
    table = model.reaction_metabolite_lookup_table()
    
    for r_id, reaction in model.reactions.items():
        if reaction.reversible:
            fwd_id = reaction.id + '_f'
            bwd_id = reaction.id + '_b'
            mapping[r_id] = (fwd_id, bwd_id)

            model.add_reaction(Reaction(fwd_id, reaction.name, False))
            model.add_reaction(Reaction(bwd_id, reaction.name, False))
            
            for m_id, coeff in table[r_id].items():
                model.stoichiometry[(m_id, fwd_id)] = coeff
                model.stoichiometry[(m_id, bwd_id)] = -coeff
            
            if isinstance(model, ConstraintBasedModel):
                lb, ub = model.bounds[r_id]
                model.set_flux_bounds(fwd_id, 0, ub)
                model.set_flux_bounds(bwd_id, 0, -lb if lb != None else None)
            
            if isinstance(model, GPRConstrainedModel):
                model.add_rule(fwd_id, model.rules[r_id])
                model.add_rule(bwd_id, model.rules[r_id])
            
            model.remove_reaction(r_id)
            
    return mapping