"""Versioned recovery-certified source measure; no change to CA dynamics."""
from fractions import Fraction

def partition(records):
    q = sum(r['transmission_confirmed'] for r in records)
    return {'Q': q, 'R': len(records)-q, 'C': len(records)}

def conjunction(values):
    values = list(values)
    return False if False in values else None if None in values else True

def fraction(value):
    return None if value is None else {'numerator': value.numerator, 'denominator': value.denominator}

def retention_bounds(d, u):
    assert 0 <= d['Q'] <= d['C'] and 0 <= u['Q'] <= u['C']
    if u['C'] == 0:
        return {'status': 'undefined_zero_detected_control', 'lower': None, 'upper': None}
    return {'status': 'bounded' if u['Q'] else 'unbounded_upper',
            'lower': fraction(Fraction(d['Q'],u['C'])),
            'upper': fraction(Fraction(d['C'],u['Q'])) if u['Q'] else None}

def panel_bounds(conditions):
    bounds = [retention_bounds(d,u) for d,u in conditions]
    if any(b['lower'] is None for b in bounds):
        return {'status':'undefined_zero_detected_control','lower':None,'upper':None}
    def value(x): return Fraction(x['numerator'],x['denominator'])
    lower = sum((value(b['lower']) for b in bounds),Fraction())/len(bounds)
    upper = None if any(b['upper'] is None for b in bounds) else sum((value(b['upper']) for b in bounds),Fraction())/len(bounds)
    return {'status':'bounded' if upper is not None else 'unbounded_upper','lower':fraction(lower),'upper':fraction(upper)}

def strict_interval_superiority(candidate, inputs):
    if candidate['lower'] is None or any(i['upper'] is None for i in inputs): return None
    value=lambda x: Fraction(x['numerator'],x['denominator'])
    return all(value(candidate['lower']) > value(i['upper']) for i in inputs)
