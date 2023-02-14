class Area:
    def __init__(self, ra_scope, dec_scope):
        # Note: rename ra and dec_set
        self.RA_SCOPE = ra_scope  # degrees
        self.DEC_SCOPE = dec_scope  # degrees
        self.RA_RANGE = abs(ra_scope[0] - ra_scope[1])
        self.DEC_RANGE = abs(dec_scope[0] - dec_scope[1])
        self.center = ((self.RA_SCOPE[0] + self.RA_SCOPE[1])/2, (self.DEC_SCOPE[0] + self.DEC_SCOPE[1])/2)  # degrees

