from math import inf
from flask_login import UserMixin
from datetime import datetime as dt
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), unique=False)
    user_handle = db.Column(db.String(100), unique=True)
    user_password = db.Column(db.String(100))
    user_role = db.Column(db.Numeric())

    def get_id(self):
        return (self.user_id)
    
class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    sponsor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sponsor_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    sponsor_industry = db.Column(db.String(100))
    sponsor_no_of_employees = db.Column(db.Numeric(100))
    sponsor_email = db.Column(db.String(100))
    sponsor_bio = db.Column(db.String(100))
    sponsor_location = db.Column(db.String(100))
    sponsor_edate = db.Column(db.String(100))
    sponsor_flaged= db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('sponsors', lazy=True))
    
class Influencer(db.Model):
    __tablename__ = 'influencer'
    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influencer_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    influencer_social_media = db.Column(db.String(100))
    influencer_no_of_followers = db.Column(db.String(100))
    influencer_email = db.Column(db.String(100))
    influencer_expertise = db.Column(db.String(100))
    influencer_bio = db.Column(db.String(100))
    influencer_location = db.Column(db.String(100))
    influencer_dob = db.Column(db.String(100))
    influencer_revenue = db.Column(db.Numeric(100),default=0)
    influencer_flaged = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('influencers', lazy=True))
    def __repr__(self):
        return f"influencer(influencer_id={self.influencer_id}, influencer_social_media={self.influencer_social_media}, influencer_no_of_followers={self.influencer_no_of_followers}, influencer_email={self.influencer_email}, influencer_bio={self.influencer_bio}, influencer_location={self.influencer_location}, influencer_dob={self.influencer_dob})"
class Adrequest(db.Model):
    __tablename__ = 'adrequest'
    adrequest_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    adrequest_status = db.Column(db.String(100),default='active')
    adrequest_payment_amount = db.Column(db.Numeric(100))
    adrequest_description = db.Column(db.String(100))
    adrequest_requerments = db.Column(db.String(100))
    adrequest_level = db.Column(db.Integer,default=0)
    message = db.Column(db.String(100))
    sponsor = db.relationship('Sponsor', backref=db.backref('adrequest', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('adrequest', lazy=True))
    campaign = db.relationship('Campaign', backref=db.backref('adrequest', lazy=True))

class Campaign(db.Model):
    __tablename__ = 'campaign'
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    adrequest_id = db.Column(db.String(100))
    campaign_status = db.Column(db.String(100),default='active')
    campaign_budget = db.Column(db.String(100),)
    campaign_description = db.Column(db.String(100),)
    campaign_domain = db.Column(db.Integer, default=0,)
    campaign_start_date = db.Column(db.String(100),)
    campaign_end_date = db.Column(db.String(100),)

    sponsor = db.relationship('Sponsor', backref=db.backref('campaign', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('campaign', lazy=True))

    def __repr__(self):
        return f"campaign(campaign_id={self.campaign_id},adrequest_id={self.adrequest_id}, campaign_status={self.campaign_status}, campaign_payment_amount={self.campaign_budget}, campaign_description={self.campaign_description}, campaign_start_date={self.campaign_start_date}, campaign_end_date={self.campaign_end_date})"
    
