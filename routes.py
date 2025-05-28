from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import datetime as dt
from models import User, Sponsor, Influencer, Adrequest, Campaign
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

routes = Blueprint('routes', __name__)
auth = Blueprint("authentication", __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("authentication.login"))

@auth.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method=="POST":
        if current_user.user_role == 1:
            inf = Influencer.query.filter_by(influencer_user_id=current_user.user_id).first()
            inf.influencer_email = request.form.get("email")
            inf.influencer_location = request.form.get("location")
            inf.influencer_bio = request.form.get("bio")
            inf.influencer_dob = request.form.get("dob")
            inf.influencer_expertise= request.form.get("expertise")
            db.session.commit()
            flash("Profile updated successfully!", category='success')
            return redirect(url_for('authentication.profile'))
        elif current_user.user_role == 2:
            sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
            sp.sponsor_name = request.form.get("name")
            sp.sponsor_industry = request.form.get("industry")
            sp.sponsor_no_of_employees = request.form.get("employees")
            sp.sponsor_email = request.form.get("email")
            sp.sponsor_location = request.form.get("location")
            sp.sponsor_bio = request.form.get("bio")
            sp.sponsor_edate = request.form.get("edate")
            db.session.commit()
            flash("Profile updated successfully!", category='success')
            return redirect(url_for('authentication.profile'))
        else:
            admin = User.query.filter_by(user_id=current_user.user_id).first()
            admin.user_name = request.form.get("name")
            db.session.commit()
            flash("Profile updated successfully!", category='success')
            return redirect(url_for('authentication.profile'))

    if current_user.user_role == 1:
        inf = Influencer.query.filter_by(influencer_user_id=current_user.user_id).first()
        return render_template("inf_profile.html", user=current_user, inf=inf)
    elif current_user.user_role == 2:
        sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
        return render_template("sp_profile.html", user=current_user, sp=sp)
    else:
        admin = User.query.filter_by(user_id=current_user.user_id).first()
        return render_template("admin_profile.html", user=current_user, admin=admin)
    
    # if not login redirect to login page

def revenue(id,payment):
    if current_user.user_role == 2:
        inf = Influencer.query.filter_by(influencer_id=id).first()
        revenue = int(inf.influencer_revenue) if inf.influencer_revenue else 0
        revenue += int(payment)
        print(id,payment,revenue)
        inf.influencer_revenue = revenue
        db.session.commit()
        return revenue
    else:
        return 0
    
@auth.route("/dashboard" , methods=['GET', 'POST'])
@login_required
def dashboard():
    campaigns = Campaign.query.all()
    for campaign in campaigns:
        d1 = dt.strptime(campaign.campaign_end_date, "%Y-%m-%d")
        d2 = dt.strptime(dt.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        d3 = dt.strptime(campaign.campaign_start_date, "%Y-%m-%d")
        delta1 = d2 - d3
        delta2 = d1 - d3
        campaign.elapceddays = delta1.days
        campaign.totaldays = delta2.days
    if current_user.user_role == 1:
        inf = Influencer.query.filter_by(influencer_user_id=current_user.user_id).first()
        adrequest = Adrequest.query.filter_by(influencer_id=inf.influencer_id).all()
        ad_req=Adrequest.query.filter_by(adrequest_requerments=inf.influencer_expertise).all()
        campaigns = Campaign.query.join(Adrequest, Campaign.campaign_id == Adrequest.campaign_id).filter(Adrequest.adrequest_level.in_([1, 3, 4])).filter(Adrequest.influencer_id==inf.influencer_id).distinct().all()
        
        for campaign in campaigns:
            d1 = dt.strptime(campaign.campaign_end_date, "%Y-%m-%d")
            d2 = dt.strptime(dt.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
            d3 = dt.strptime(campaign.campaign_start_date, "%Y-%m-%d")
            delta1 = d2 - d3
            delta2 = d1 - d3
            campaign.elapceddays = delta1.days
            campaign.totaldays = delta2.days
        return render_template("inf_dashboard.html", user=current_user, inf=inf ,Adrequest=adrequest,ads=ad_req,campaigns=campaigns)
    elif current_user.user_role == 2:
        sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
        campaign = Campaign.query.filter_by(sponsor_id=sp.sponsor_id).all()
        adrequest = Adrequest.query.filter_by(sponsor_id=sp.sponsor_id).all()
        pvads= Adrequest.query.filter_by(adrequest_level=5).filter_by(sponsor_id=sp.sponsor_id).all()
        return render_template("sp_dashboard.html", user=current_user, sp=sp, Campaign=campaign,Adrequest=adrequest,pvads=pvads)
    
    elif current_user.user_role == 3:
        admin = User.query.filter_by(user_id=current_user.user_id).first()
        sp = Sponsor.query.all()
        inf = Influencer.query.all()
        campaign = Campaign.query.all()
        adrequest = Adrequest.query.all()
        return render_template("admin_dashboard.html", user=current_user,sp=sp,inf=inf,campaign=campaign,adrequest=adrequest, admin=admin)
    else:
        return "You are not authorized to view this page."

@auth.route("/flagged" , methods=['GET', 'POST'])
@login_required
def flagged():
    if request.method == 'POST':
        if current_user.user_role == 3:
            sp=request.form.get("sponsor_id")
            inf=request.form.get("influencer_id")
            camp=request.form.get("campaign_id")
            adreq=request.form.get("adrequest_id")
            value=request.form.get("value")
            sponsor = Sponsor.query.filter_by(sponsor_id=sp).first()
            influencer = Influencer.query.filter_by(influencer_id=inf).first()
            campaign = Campaign.query.filter_by(campaign_id=camp).first()
            adrequest = Adrequest.query.filter_by(adrequest_id=adreq).first()
            if value == "True":
                if sponsor:
                    sponsor.sponsor_flaged = True
                if influencer:
                    influencer.influencer_flaged = True
                if campaign:
                    campaign.campaign_flaged = True
                if adrequest:
                    adrequest.adrequest_flaged = True
                db.session.commit()
            elif value == "False":
                if sponsor:
                    sponsor.sponsor_flaged = False
                if influencer:
                    influencer.influencer_flaged = False
                if campaign:
                    campaign.campaign_flaged = False
                if adrequest:
                    adrequest.adrequest_flaged = False
                db.session.commit()
            else:
                return "You are not authorized"
            flash("Flagged status updated successfully!", category='success')
            return redirect(url_for('authentication.dashboard'))
    else:
        return "You are not authorized to view this page."

@auth.route("/dashboard/campaigns" ,  methods=['GET', 'POST'])
@login_required
def campaigns():
    campaigns = Campaign.query.all()
    for campaign in campaigns:
        d1 = dt.strptime(campaign.campaign_end_date, "%Y-%m-%d")
        d2 = dt.strptime(dt.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        d3 = dt.strptime(campaign.campaign_start_date, "%Y-%m-%d")
        delta1 = d2 - d3
        delta2 = d1 - d3
        if delta1.days-1 == delta2.days:
            return redirect(url_for('authentication.delete_campaign',id=campaign.campaign_id))
        campaign.elapceddays = delta1.days
        campaign.totaldays = delta2.days
        
    if request.method == 'POST':
        if current_user.user_role == 2:
            sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
            description = request.form.get("description")
            start_date = request.form.get("sdate")
            end_date = request.form.get("edate")
            budget = request.form.get("budget")
            domain = request.form.get("domain")
            id=request.form.get("campaign_id_u")

            campaign = Campaign.query.get(id)
            if campaign:
                campaign.campaign_description = description
                campaign.campaign_start_date = start_date
                campaign.campaign_end_date = end_date
                campaign.campaign_budget = budget
                campaign.campaign_domain = domain
                db.session.commit()
                flash("Campaign updated successfully!", category='success')
                return redirect(url_for('authentication.campaigns'))
            
            else:
                new_campaign = Campaign(
                    sponsor_id=sp.sponsor_id, 
                    campaign_description=description,
                    campaign_budget=budget,
                    campaign_domain=domain,
                    campaign_start_date=start_date, 
                    campaign_end_date=end_date
                )            
                db.session.add(new_campaign)
                db.session.commit()
                flash("Campaign created successfully!", category='success')
                return redirect(url_for('authentication.campaigns'))
        

    if current_user.user_role == 2:
        sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
        campaign = Campaign.query.filter_by(sponsor_id=sp.sponsor_id).all()
        last_campaign = Campaign.query.order_by(Campaign.campaign_id.desc()).first()
        ls_camp_id = last_campaign.campaign_id if last_campaign else 0
        return render_template("sp_campaigns.html", user=current_user, sp=sp ,Campaign=campaign, last_camp_id=ls_camp_id)
    elif current_user.user_role == 1:
        inf = Influencer.query.filter_by(influencer_user_id=current_user.user_id).first()
        adrequest = Adrequest.query.filter_by(influencer_id=inf.influencer_id).all()
        campaigns = Campaign.query.all()
        return render_template("inf_campaigns.html", user=current_user, inf=inf, Adrequest=adrequest, campaign=campaigns)
    else:
        return "You are not authorized to view this page."

@auth.route("/stats" ,  methods=['GET', 'POST'])
@login_required
def stats():
    if current_user.user_role == 3:
        sp=Sponsor.query.all()
        inf=Influencer.query.all()
        sp1 = Sponsor.query.filter_by(sponsor_flaged=True).all()
        inf1 = Influencer.query.filter_by(influencer_flaged=True).all()
        campaign = Campaign.query.all()
        adrequest = Adrequest()
        adrequest.p = len(Adrequest.query.filter_by(adrequest_level=0).all())
        adrequest.a=len(Adrequest.query.filter_by(adrequest_level=1).all())
        adrequest.r=len(Adrequest.query.filter_by(adrequest_level=2).all())
        adrequest.c=len(Adrequest.query.filter_by(adrequest_level=3).all())
        adrequest.pr=len(Adrequest.query.filter_by(adrequest_level=4).all())

        elements = [
            {"name": influencer.user.user_handle, "Revenue": influencer.influencer_revenue, "color": "#b87333"}
            for influencer in inf
        ]
        return render_template("admin_stats.html",elements=elements, user=current_user,infv=inf,sp=len(sp)-len(sp1),inf=len(inf)-len(inf1),flag=len(sp1)+len(inf1),campaign=len(campaign),adrequests=adrequest)
    
    elif current_user.user_role == 2:
        inf = Influencer.query.all()
        ads=Adrequest.query.all()
        count1 = {j: 0 for j in range(0, 13)}
        count2 = {j: 0 for j in range(0, 13)}

        for a in ads:
            level = int(a.adrequest_requerments) if a.adrequest_requerments else '0'
            if level in count1:
                count1[level] += 1

        for i in inf:
            expertise = int(i.influencer_expertise) if i.influencer_expertise else '0'
            if expertise in count2:
                count2[expertise] += 1

        return render_template("sp_stats.html", user=current_user, inf=inf,count1=count1,count2=count2)
    elif current_user.user_role == 1:
        sp = Sponsor.query.all()
        ads=Adrequest.query.all()
        inf=Influencer.query.all()
        count = {j: 0 for j in range(0, 13)}
        count2 = {j: 0 for j in range(0, 13)}


        for a in ads:
            level = int(a.adrequest_requerments) if a.adrequest_requerments else '0'
            if level in count:
                count[level] += 1
        
        for i in inf:
            expertise = int(i.influencer_expertise) if i.influencer_expertise else '0'
            if expertise in count2:
                count2[expertise] += 1


        return render_template("inf_stats.html", user=current_user, sp=sp,count=count, count2=count2)
    else:
        return "You are not authorized to view this page."

@auth.route("/about" ,  methods=['GET', 'POST'])
@login_required
def about():
    return render_template("about.html")


@auth.route("/find" ,  methods=['GET', 'POST'])
@login_required
def find():
    if current_user.user_role == 2:
        sp = Sponsor.query.all()
        inf = Influencer.query.all()
        search_result = None
        if request.method == 'POST':
            user_handle = request.form.get('user_handle')
            expertise = request.form.get('expertise')
            if user_handle:
                search_result = Influencer.query.join(User).filter(User.user_handle == user_handle).first()
            elif expertise:
                search_result = Influencer.query.filter(Influencer.influencer_expertise==expertise).first()
        return render_template("sp_find.html", user=current_user, sp=sp, Influencer=inf, search_result=search_result)
    elif current_user.user_role == 1:
        sp = Sponsor.query.all()
        inf = Influencer.query.all()
        search_result = None
        if request.method == 'POST':
            user_handle = request.form.get('user_handle')
            domain = request.form.get('domain')
            if user_handle:
                search_result = Sponsor.query.join(User).filter(User.user_handle == user_handle).first()
            elif domain:
                search_result = Sponsor.query.filter(Sponsor.sponsor_industry==domain).first()

        return render_template("inf_find.html", user=current_user, sp=sp, Influencer=inf, search_result=search_result)
        


        
    
@auth.route("/dashboard/campaigns/delete/<int:id>", methods=['GET', 'POST'])
@login_required
def delete_campaign(id):
    if current_user.user_role == 2:
        campaign = Campaign.query.filter_by(campaign_id=id).first()
        if campaign:
            adrequests = Adrequest.query.filter_by(campaign_id=id).all()
            for adrequest in adrequests:
                db.session.delete(adrequest)
        db.session.delete(campaign)
        db.session.commit()
        flash("Campaign deleted successfully!", category='success')
        return redirect(url_for('authentication.campaigns'))
    elif current_user.user_role == 3:
        campaign = Campaign.query.filter_by(campaign_id=id).first()
        if campaign:
            adrequests = Adrequest.query.filter_by(campaign_id=id).all()
            for adrequest in adrequests:
                db.session.delete(adrequest)
            db.session.delete(campaign)
            db.session.commit()
            flash("Campaign deleted successfully!", category='success')
            return redirect(url_for('authentication.dashboard'))
        else:
            flash("Campaign not found.", category='error')
    else:
        return "You are not authorized to view this page."
    
@auth.route("/dashboard/adrequests/<int:id>" ,  methods=['GET', 'POST'])
@login_required
def adrequests(id):
    if request.method == 'POST':
        if current_user.user_role == 1:
            if request.form.get("visit")=="False":
                inf = Influencer.query.filter_by(influencer_user_id=current_user.user_id).first()
                description = request.form.get("description")
                payment = request.form.get("budget")
                requirements = request.form.get("req")
                aid=request.form.get("adrequest_id_u")
                camp=Campaign.query.filter_by(campaign_id=id).first()

                adrequest = Adrequest.query.get(aid)
                if adrequest:
                    adrequest.adrequest_description = description
                    adrequest.adrequest_payment_amount = payment
                    adrequest.adrequest_requerments = requirements
                    db.session.commit()
                    flash("Adrequest updated successfully!", category='success')
                    return redirect(url_for('authentication.adrequests', id=id))
                
                else:
                    new_adrequest = Adrequest(
                        influencer_id=inf.influencer_id, 
                        adrequest_description=description,
                        adrequest_payment_amount=payment,
                        adrequest_requerments=requirements,
                        adrequest_level=5,
                        campaign_id=id,
                        sponsor_id=camp.sponsor_id
                    )            
                    db.session.add(new_adrequest)
                    db.session.commit()
                    flash("Adrequest created successfully!", category='success')
                    return redirect(url_for('authentication.adrequests',id=id))
            
            elif request.form.get("visit")=="True":
                inf = Influencer.query.filter_by(influencer_user_id=current_user.user_id).first()
                adrequest = Adrequest.query.filter_by(influencer_id=inf.influencer_id).all()

                last_adrequest = Adrequest.query.order_by(Adrequest.adrequest_id.desc()).first()
                ls_adreq_id = last_adrequest.adrequest_id if last_adrequest else 0
                campaign = Campaign.query.filter_by(campaign_id=id).first()
                return render_template("inf_adrequest.html", user=current_user,campaign=campaign, inf=inf ,Adrequest=adrequest, last_adreq_id=ls_adreq_id,dt=dt)

        elif current_user.user_role == 2:
            if request.form.get("visit")=="False":
                sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
                description = request.form.get("description")
                payment = request.form.get("budget")
                camp = request.form.get("camp")
                requirements = request.form.get("req")
                aid=request.form.get("adrequest_id_u")
                inf=request.form.get("influencer")
                
                print(requirements)
                adrequest = Adrequest.query.get(aid)
                if adrequest:
                    adrequest.adrequest_description = description
                    adrequest.adrequest_payment_amount = payment
                    adrequest.adrequest_requerments = requirements
                    db.session.commit()
                    flash("Adrequest updated successfully!", category='success')
                    return redirect(url_for('authentication.adrequests',id=id))
                
                else:
                    new_adrequest = Adrequest(
                        sponsor_id=sp.sponsor_id, 
                        adrequest_description=description,
                        adrequest_payment_amount=payment,
                        adrequest_requerments=requirements,
                        campaign_id=camp,
                        influencer_id=inf
                    )
                    print(camp)
                    db.session.add(new_adrequest)
                    db.session.commit()
                    campaign = Campaign.query.filter_by(campaign_id=camp).first()
                    if campaign.adrequest_id:
                        adrequest_ids = list(map(int, campaign.adrequest_id.split(',')))
                        adrequest_ids.append(new_adrequest.adrequest_id)
                        campaign.adrequest_id = ','.join(map(str, adrequest_ids))
                    else:
                        campaign.adrequest_id=str(new_adrequest.adrequest_id)
                    print(campaign.adrequest_id)
                    db.session.commit()
                    flash("Adrequest created successfully!", category='success')
                    return redirect(url_for('authentication.adrequests', id=id))
                
            elif request.form.get("visit")=="True":
                sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
                adrequests = Adrequest.query.filter_by(sponsor_id=sp.sponsor_id).all()
                last_adrequest = Adrequest.query.order_by(Adrequest.adrequest_id.desc()).first()
                ls_adreq_id = last_adrequest.adrequest_id if last_adrequest else 0
                campaign= Campaign.query.filter_by(campaign_id=id).first()
                influencers = Influencer.query.all()
                ads=[]
                if campaign.adrequest_id:
                    for n in campaign.adrequest_id:
                        ads.append(n)

                return render_template("sp_adrequest.html", user=current_user, sp=sp, campaign=campaign,ads=ads ,Adrequest=adrequests, last_adreq_id=ls_adreq_id, influencers=influencers)
        
            else:
                return "You are not authorized to view this page."
        else:
            return "You are not authorized to view this page."
    elif request.method != 'POST':
        if current_user.user_role == 1:
            inf = Influencer.query.filter_by(influencer_user_id=current_user.user_id).first()
            adrequest = Adrequest.query.filter_by(influencer_id=inf.influencer_id).all()
            last_adrequest = Adrequest.query.order_by(Adrequest.adrequest_id.desc()).first()
            ls_adreq_id = last_adrequest.adrequest_id if last_adrequest else 0
            campaign = Campaign.query.filter_by(campaign_id=id).first()
            return render_template("inf_adrequest.html", user=current_user, inf=inf ,campaign=campaign,Adrequest=adrequest, last_adreq_id=ls_adreq_id,dt=dt)
        elif current_user.user_role == 2:
            sp = Sponsor.query.filter_by(sponsor_user_id=current_user.user_id).first()
            adrequests = Adrequest.query.filter_by(sponsor_id=sp.sponsor_id).all()
            last_adrequest = Adrequest.query.order_by(Adrequest.adrequest_id.desc()).first()
            ls_adreq_id = last_adrequest.adrequest_id if last_adrequest else 0
            campaign= Campaign.query.filter_by(campaign_id=id).first()
            influencers = Influencer.query.all()
            ads=[]
            if campaign.adrequest_id:
                for n in campaign.adrequest_id:
                    ads.append(n)
            return render_template("sp_adrequest.html", user=current_user, sp=sp, campaign=campaign,ads=ads ,Adrequest=adrequests, last_adreq_id=ls_adreq_id, influencers=influencers)
        else:
            return "You are not authorized to view this page."
    else:
        return "You are not authorized to view this page."

@auth.route('/dashboard/adrequests/level', methods=['POST'])
@login_required
def adrequest_level():
    if current_user.user_role == 1:
        adrequest_id = request.form.get("adrequest_id")
        level = request.form.get("level")
        inf=request.form.get("influencer_id")
        adrequest = Adrequest.query.get(adrequest_id)
        message=request.form.get("message")
        print(adrequest, level,"na",message)
        if adrequest:
            adrequest.adrequest_level = level
            if adrequest.adrequest_level == 1:
                adrequest.adrequest_requerments = inf.influencer_expertise
            if inf:
                adrequest.influencer_id=inf
            if message:
                adrequest.message=message
            db.session.commit()
            
            flash("Adrequest Accepted", category='success')
        else:
            flash("Adrequest not found.", category='error')
        return redirect(url_for('authentication.dashboard'))

    if current_user.user_role == 2:
        adrequest_id = request.form.get("adrequest_id")
        level = request.form.get("level")
        adrequest = Adrequest.query.get(adrequest_id)
        if adrequest:
            adrequest.adrequest_level = level
            db.session.commit()
            if int(level) == 4:
                revenue(adrequest.influencer_id,adrequest.adrequest_payment_amount)
                print('re')
            flash("Adrequest status updated successfully!", category='success')
        else:
            flash("Adrequest not found.", category='error')
        if level == "2":
            return redirect(url_for('authentication.adrequests', id=adrequest.campaign_id))
        elif level == "4":
            return redirect(url_for('authentication.campaigns'))
        else:
            return redirect(url_for('authentication.dashboard'))
    else:
        return "You are not authorized to perform this action."

@auth.route('/dashboard/adrequests/delete_adrequest/<int:id>/<int:cd>', methods=['POST'])
@login_required
def delete_adrequest(id, cd):
    if current_user.user_role == 1:
        adrequest = Adrequest.query.filter_by(adrequest_id=id).first()
        if adrequest:
            db.session.delete(adrequest)
            db.session.commit()
            flash("Adrequest deleted successfully!", category='success')
        else:
            flash("Adrequest not found.", category='error')
        return redirect(url_for('authentication.dashboard'))
    elif current_user.user_role == 2:
        adrequest = Adrequest.query.filter_by(adrequest_id=id).first()
        campaigns = Campaign.query.filter_by(campaign_id=cd).first()
        if adrequest and campaigns:
            adrequest_ids = list(map(int, campaigns.adrequest_id.split(',')))
            if id in adrequest_ids:
                adrequest_ids.remove(id)
                campaigns.adrequest_id = ','.join(map(str, adrequest_ids))
                db.session.commit()
            db.session.delete(adrequest)
            db.session.commit()
            flash("Adrequest deleted successfully!", category='success')
        else:
            flash("Adrequest not found.", category='error')
        return redirect(url_for('authentication.adrequests',id=cd))
    elif current_user.user_role == 3:
        ads=request.form.get("adrequest_id")
        adrequest = Adrequest.query.filter_by(adrequest_id=ads).first()
        if adrequest:
            db.session.delete(adrequest)
            db.session.commit()
            flash("Adrequest deleted successfully!", category='success')
        else:
            flash("Adrequest not found.", category='error')
    else:
        return "You are not authorized to perform this action."

@auth.route("/login", methods=['GET', 'POST'])
def login():
    warnings = []
    if request.method == 'POST':
        uname = request.form.get("username")
        password = request.form.get("pwd")

        auth_user = User.query.filter_by(user_handle=uname).first()
        if auth_user:
            sp = Sponsor.query.filter_by(sponsor_user_id=auth_user.user_id).first()
            inf = Influencer.query.filter_by(influencer_user_id=auth_user.user_id).first()
            if check_password_hash(auth_user.user_password, password):
                if auth_user.user_role == 1:
                    if not inf.influencer_flaged:
                        flash("Login successful! As Influencer", category='success')
                        login_user(auth_user, remember=True)
                        return redirect(url_for('authentication.profile'))
                    else:
                        warnings.append('Your account has been flagged.')   
                        return render_template("login.html", customer_user=current_user, warnings=warnings)
                elif auth_user.user_role == 2:
                    if not sp.sponsor_flaged:
                        flash("Login successful! As Sponsor", category='success')
                        login_user(auth_user, remember=True)
                        return redirect(url_for('authentication.profile'))
                    else:
                        warnings.append('Your account has been flagged.')
                        return render_template("login.html", customer_user=current_user, warnings=warnings)
                else:
                    flash("Login successful! As Admin", category='success')
                    login_user(auth_user, remember=True)
                    return redirect(url_for('authentication.dashboard'))
            else:
                warnings.append('Incorrect password.')
        else:
            warnings.append('Username not found.')
    
    admin_u = "admin"
    admin_p = "admin"

    admin = User.query.filter_by(user_name=admin_u).filter_by(user_role=3).first()
    if not admin:
        new_user = User(user_name="admin", user_handle="admin", user_password=generate_password_hash(admin_p), user_role=3)
        db.session.add(new_user)
        db.session.commit()

    return render_template("login.html", customer_user=current_user, warnings=warnings)

@auth.route("/signup_influencer", methods=['GET', 'POST'])
def inf_sign_up():
    warnings = []
    if "user_id" in session:
        flash("You are already logged in as Influencer!", category='error')
        return redirect(url_for('authentication.profile'))
    elif request.method == 'POST':
        name = request.form.get("name")
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        pwdConfirm = request.form.get("confpwd")
        no_followers = request.form.get("followers")
        social_media= request.form.getlist("social_media[]")
        sm=""

        username_exists = User.query.filter_by(user_handle=username).first()
        
        
        def contains_special_character(pwd):
            special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
            return any(char in special_characters for char in pwd)
        if not username:
            warnings.append('Please enter a username.')
        if not name:
            warnings.append('Please enter a name.')
        if username_exists:
            warnings.append('This username has already been chosen, please choose another one.')
        if pwd != pwdConfirm:
            warnings.append('Passwords do not match.')
        if not contains_special_character(pwd):
            warnings.append('Password must contain at least one special character.')
        if len(pwd) < 6:
            warnings.append('Password must be at least 6 characters long.')
        for i in range(len(social_media)):
                sm=sm+str(social_media[i])
        # 1 =instagram, 2=twitter, 3=facebook,4=youtube

        if not warnings:
            new_user = User(user_name=name, user_handle=username, user_password=generate_password_hash(pwd), user_role=1)
            db.session.add(new_user)
            db.session.commit()
            new_influencer = Influencer(influencer_user_id=new_user.user_id, influencer_social_media=sm, influencer_no_of_followers=no_followers)
            db.session.add(new_influencer)
            db.session.commit()
            flash("Account created successfully!", category='success')
            return redirect(url_for('authentication.login'))
    return render_template("inf_signup.html", customer_user=current_user, warnings=warnings)

@auth.route("/signup_sponsor", methods=['GET', 'POST'])
def sp_sign_up():
    warnings = []
    if "user_id" in session:
        flash("You are already logged in as Sponsor!", category='error')
        return redirect(url_for('authentication.profile'))
    if request.method == 'POST':
        name = request.form.get("name")
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        pwdConfirm = request.form.get("confpwd")
        industry = request.form.get("industry")
        no_employees = request.form.get("employees")

        username_exists = User.query.filter_by(user_handle=username).first()
        
        def contains_special_character(pwd):
            special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
            return any(char in special_characters for char in pwd)

        if username_exists:
            warnings.append('This username has already been chosen, please choose another one.')
        if pwd != pwdConfirm:
            warnings.append('Passwords do not match.')
        if not contains_special_character(pwd):
            warnings.append('Password must contain at least one special character.')
        if len(pwd) < 6:
            warnings.append('Password must be at least 6 characters long.')

        if not warnings:
            new_user = User(user_name=name, user_handle=username, user_password=generate_password_hash(pwd), user_role=2)
            db.session.add(new_user)
            db.session.commit()
            new_sponsor = Sponsor(sponsor_user_id=new_user.user_id, sponsor_industry=industry, sponsor_no_of_employees=no_employees)
            db.session.add(new_sponsor)
            db.session.commit()
            flash("Account created successfully!", category='success')
            return redirect(url_for('authentication.login'))

    return render_template("sp_signup.html", customer_user=current_user, warnings=warnings)

@auth.route("/delete_user", methods=['GET', 'POST'])
@login_required
def delete_user():
    if request.method == 'POST':
        if current_user.user_role == 3:
            sp=request.form.get("sponsor_id")
            inf=request.form.get("influencer_id")
            camp=request.form.get("campaign_id")
            adreq=request.form.get("adrequest_id")
            if sp:
                sponsor = Sponsor.query.filter_by(sponsor_id=sp).first()
                user = User.query.filter_by(user_id=sponsor.sponsor_user_id).first()
                if sponsor:
                    db.session.delete(sponsor)
                    db.session.delete(user)
                    db.session.commit()
            if inf:
                influencer = Influencer.query.filter_by(influencer_id=inf).first()
                user = User.query.filter_by(user_id=influencer.influencer_user_id).first()
                if influencer:
                    db.session.delete(influencer)
                    db.session.delete(user)
                    db.session.commit()
            if camp:
                campaign = Campaign.query.filter_by(campaign_id=camp).first()
                if campaign:
                    db.session.delete(campaign)
                    db.session.commit()
            if adreq:
                adrequest = Adrequest.query.filter_by(adrequest_id=adreq).first()
                if adrequest:
                    db.session.delete(adrequest)
                    db.session.commit()
            flash("User deleted successfully!", category='success')
            return redirect(url_for('authentication.dashboard'))
        else:
            return "You are not authorized to perform this action."
    else:
        return "You are not authorized to perform this action."


    


    
