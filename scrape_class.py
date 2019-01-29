#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 18:50:12 2019

@author: grant
"""

class scrape_federal_reserve:
    
    rand = 5
    
    def __init__(self,code_class,random):
        self.country_codes = code_class
        self.random = random
        
        
    def display_codes(self):
        
        codes = self.country_codes.get_codes()
        
        if self.random == False:
            pass
        else:
            codes = codes.sample(n=self.rand)
            
        return(codes)
    
    #this should only select a small random number of countries to test the webscape
    @classmethod
    def set_random(cls,amount):
        cls.rand=amount
