# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 12:00:23 2013

@author: Robin van Rijn
"""

from sqlalchemy import Column, Integer, Sequence, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from dbconnection import engine, session, Base
from models.answer import AnswerModel
from basemodel import BaseEntity


class Review(Base, BaseEntity):
    __tablename__ = 'Review'
    
    answer_id = Column(Integer, ForeignKey('answer.id', ondelete='CASCADE'))
    user_id = Column(String)
    text = Column(String)
    rating = Column(Integer)
    
    def __init__(self, answer_id, user_id, rating, text):
        self.answer_id = answer_id
        self.user_id = user_id
        self.rating = rating
        self.text = text
    
    def __repr__(self):
        return "<Review(aid='%d', uid='%s', '%s')" % (self.answer_id,
            self.user_id, self.text)
    
    @staticmethod
    def add(answer_id, user_id, rating, text):
        if session.query(Review).filter(Review.answer_id == answer_id,
                Review.user_id == user_id).first() is None:
            session.add(Review(answer_id, user_id, text, rating))
            session.commit()
            
    @staticmethod
    def delete(answer_id, user_id):
        for review in session.query(Review).filter(
                Review.answer_id == answer_id, Review.user_id == user_id):
            session.delete(review)
            session.commit()
    
    @staticmethod
    def get(answer_id, user_id):
        return session.query(Review).filter(Review.answer_id == answer_id,
            Review.user_id == user_id).all()
            
    @staticmethod
    def get_list(answer_id):
        return session.query(Review).filter(Review.answer_id==answer_id).all()

Base.metadata.create_all(engine)