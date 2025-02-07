import time
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_from_directory
from flask import abort, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from .Security_Features_Function.Encryption import encrypt_data, decrypt_data
from .Security_Features_Function.Contact_Anonymization import anonymize_old_records
from .payment_utils import determine_plan_details, extract_payment_method
from .models import *
from .auth import current_user
import random
import os
from datetime import timedelta, datetime


route = Blueprint('route', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@route.route('/')
def index():
    return render_template("home/index.html")


@route.route('/plans')
def Plans_Overview():
    return render_template("home/Plans.html")


@route.route('/policy')
def PolicyTerms():
    return render_template("home/Policy&Terms.html")


@route.route('/contact', methods=["GET", "POST"])
def ContactSupport():
    anonymize_old_records()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not name or not email or not subject or not message:
            flash("All fields are required!", "danger")
            return redirect(url_for('contact'))

        try:
            new_message = ContactMessage(name=name, email=email, subject=subject, message=message)
            db.session.add(new_message)
            db.session.commit()
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again later.", "danger")
            print(f"Error: {e}")

        return redirect(url_for('route.ContactSupport'))

    return render_template('home/Contact.html')


@route.route('/essential_plan')
@login_required
def Essential_Plan():
    if current_user:
        return render_template("Login-home/Essential_Plan.html")


@route.route('/enhanced_plan')
@login_required
def Enhanced_Plan():
    if current_user:
        return render_template("Login-home/Enhanced_Plan.html")


@route.route('/elite_plan')
@login_required
def Elite_Plan():
    if current_user:
        return render_template("Login-home/Elite_Plan.html")


@route.route('/plus_plan')
@login_required
def Plus_Plan():
    if current_user:
        return render_template("Login-home/Plus_Plan.html")


@route.route('/purchase/Step_1/<plan_id>', methods=['GET', 'POST'])
@login_required
def personal_info(plan_id):
    if plan_id not in ['elite', 'enhanced', 'plus', 'essential']:
        flash("Invalid plan selected. Please select a valid plan.", "danger")
        return redirect(url_for('route.Plans_Overview'))

    session['purchase_step'] = 1
    session['plan_id'] = plan_id

    if request.method == 'POST':
        try:
            street_address = request.form.get('street')
            city = request.form.get('city')
            postal_code = request.form.get('postal')
            country = request.form.get('country')
            consent = request.form.get('consent')

            if not street_address or not postal_code or not consent:
                flash("All fields are required. Please fill in the missing details.", "danger")
                return redirect(url_for('route.personal_info', plan_id=plan_id))

            time.sleep(1)

            encrypted_postal_code = encrypt_data(postal_code, current_user.id)

            billing_address = BillingAddress(user_id=current_user.id, fname=current_user.first_name, email=current_user.email, street_address=street_address, city=city, postal_code=encrypted_postal_code, country=country, created_at=func.current_timestamp())

            db.session.add(billing_address)
            db.session.commit()

            session['purchase_step'] = 2

            return redirect(url_for('route.payment_info', plan_id=plan_id))

        except Exception:
            db.session.rollback()
            flash('An error occurred while saving your information. Please try again.', 'error')
            return redirect(url_for('route.personal_info', plan_id=plan_id))

    return render_template("Login-home/Purchase_Personal_Info.html", current_user=current_user, plan_id=plan_id)


@route.route('/purchase/Step_2/<plan_id>', methods=['GET', 'POST'])
@login_required
def payment_info(plan_id):
    if session.get('purchase_step') != 2 or session.get('plan_id') != plan_id:
        flash("Please complete the previous steps first.", "warning")
        return redirect(url_for('route.personal_info', plan_id=plan_id))

    if request.method == 'POST':
        try:
            cardholder_name = request.form.get('ch-name')
            card_number = request.form.get('c-num')
            expiration_date = request.form.get('e-date')
            cvv = request.form.get('cvv')
            consent = request.form.get('consent')

            if not cardholder_name or not card_number or not expiration_date or not cvv or not consent:
                flash("All fields are required. Please fill in the missing details.", "danger")
                return redirect(url_for('route.payment_info', plan_id=plan_id))

            time.sleep(5)

            encrypted_cvv = encrypt_data(cvv, current_user.id)
            encrypted_card_num = encrypt_data(card_number, current_user.id)

            payment = Payment(user_id=current_user.id, fname=current_user.first_name, email=current_user.email, cardholder_name=cardholder_name, card_number=encrypted_card_num, expiration_date=expiration_date, cvv=encrypted_cvv, created_at=func.current_timestamp())

            db.session.add(payment)
            db.session.commit()

            session['purchase_step'] = 3

            policy_num = "POL" + str(random.randint(10000, 999999))
            while Purchase_details.query.filter_by(policy_num=policy_num).first():
                policy_num = "POL" + str(random.randint(10000, 999999))

            payment_method = extract_payment_method(card_number)

            try:
                plan_details = determine_plan_details(plan_id)
                plan_name = plan_details['name']
                plan_price = plan_details['price']
            except ValueError:
                flash("Invalid plan selected.", "danger")
                return redirect(url_for('route.payment_info', plan_id=plan_id))

            effective_date = datetime.now()
            expiration_date = effective_date + timedelta(days=365)

            billing_address = BillingAddress.query.filter_by(user_id=current_user.id).order_by(BillingAddress.created_at.desc()).first()

            purchase = Purchase_details(first_name=current_user.first_name, email=current_user.email, plan_name=plan_name, plan_price=plan_price, policy_num=policy_num, effective_date=effective_date, expiration_date=expiration_date, payment_method=payment_method, payment_id=payment.id, address_id=billing_address.id)

            db.session.add(purchase)
            db.session.commit()

            return redirect(url_for('route.purchase_confirmation', plan_id=plan_id))

        except Exception:
            db.session.rollback()
            flash("An error occurred while processing your payment. Please try again.", "error")
            return redirect(url_for('route.payment_info', plan_id=plan_id))

    return render_template("Login-home/Purchase_Payment_Info.html", plan_id=plan_id)


@route.route('/purchase/confirmation/<plan_id>', methods=['GET'])
@login_required
def purchase_confirmation(plan_id):
    if session.get('purchase_step') != 3 or session.get('plan_id') != plan_id:
        flash("Please complete the previous steps first.", "warning")
        return redirect(url_for('route.personal_info', plan_id=plan_id))

    purchase = Purchase_details.query.filter_by(email=current_user.email).order_by(Purchase_details.id.desc()).first()

    if not purchase:
        flash("No purchase record found. Please try again.", "danger")
        return redirect(url_for('route.payment_info', plan_id=plan_id))

    session.pop('purchase_step', None)
    session.pop('plan_id', None)

    return render_template("Login-home/Purchase_Confirmation.html", purchase=purchase, current_user=current_user)


@route.route('/purchased_plan', methods=['GET'])
@login_required
def purchased_plan():
    plan = Purchase_details.query.filter_by(email=current_user.email).all()

    plan_statuses = []

    for plan in plan:
        if isinstance(plan.expiration_date, datetime):
            status = "Active" if datetime.now() < plan.expiration_date else "Expired"

        token = current_app.serializer.dumps({'policy_num': plan.policy_num})

        plan_statuses.append({
            "plan": plan,
            "status": status,
            "token": token
        })

    return render_template("user/Purchase_Plans_list.html", current_user=current_user, plan_statuses=plan_statuses)


@route.route('/purchased_plan_details/<string:token>', methods=['GET'])
@login_required
def purchased_plan_details(token):
    try:
        data = current_app.serializer.loads(token)
        policy_num = data['policy_num']
    except Exception:
        abort(400, "Invalid or expired token.")

    purchase = Purchase_details.query.filter_by(policy_num=policy_num, email=current_user.email).first()

    return render_template("user/Purchase_Info.html", purchase=purchase, current_user=current_user, token=token)


@route.route('/billing_info/<string:token>', methods=['GET'])
@login_required
def billing_info(token):
    try:
        data = current_app.serializer.loads(token)
        policy_num = data['policy_num']
    except Exception:
        abort(400, "Invalid or expired token.")

    purchase_details = Purchase_details.query.filter_by(policy_num=policy_num, email=current_user.email).first()

    billing_address = BillingAddress.query.filter_by(id=purchase_details.address_id).first()
    payment = Payment.query.filter_by(id=purchase_details.payment_id).first()

    decrypted_postal_code = decrypt_data(billing_address.postal_code)
    decrypted_cvv = decrypt_data(payment.cvv)
    decrypted_card_num = decrypt_data(payment.card_number)

    return render_template("user/Billing_Info.html", current_user=current_user, billing_address=billing_address, payment=payment, card_num=decrypted_card_num, postal_code=decrypted_postal_code, cvv=decrypted_cvv, token=token)


@route.route('/claims/Step_1/<string:token>', methods=['GET', 'POST'])
@login_required
def general_info(token):
    try:
        data = current_app.serializer.loads(token)
        policy_num_token = data['policy_num']
    except Exception:
        abort(400, "Invalid or expired token.")

    if request.method == 'POST':
        reason_for_claim = request.form.get('reason')
        date_of_claim = datetime.now()
        consent = request.form.get('consent')

        if not reason_for_claim or not consent:
            flash("Please fill in all required fields and agree to the privacy policy.", "danger")
            return redirect(url_for('route.general_info'))

        time.sleep(1)

        claim = Claim_general_info(
            user_id=current_user.id,
            first_name=current_user.first_name,
            email=current_user.email,
            policy_num=policy_num_token,
            reason_for_claim=reason_for_claim,
            date_of_claim=date_of_claim,
        )

        db.session.add(claim)
        db.session.commit()

        new_token = current_app.serializer.dumps({'policy_num': policy_num_token})

        return redirect(url_for('route.specific_info', token=new_token))

    return render_template("Login-home/Claim_General_Info.html", current_user=current_user, token=policy_num_token, policy_num=policy_num_token, today_date=datetime.now().strftime('%Y-%m-%d'))


@route.route('/claims/Step_2/<string:token>', methods=['GET', 'POST'])
@login_required
def specific_info(token):
    try:
        data = current_app.serializer.loads(token)
        policy_num_token = data['policy_num']
    except Exception:
        abort(400, "Invalid or expired token.")

    if request.method == 'POST':
        hospital_name = request.form.get('hospital_name')
        location = request.form.get('hc_address')
        medical_receipts = request.files.get('medical_receipts')

        if not hospital_name or not location:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('route.specific_info', token=policy_num_token))

        time.sleep(1)

        saved_files = {}

        if medical_receipts:
            MAX_FILE_SIZE = 5 * 1024 * 1024

            if len(medical_receipts.read()) > MAX_FILE_SIZE:
                flash(f"The file for medical receipt is too large. Maximum allowed size is 5MB.", "danger")
                return redirect(url_for('route.specific_info', token=token))

            medical_receipts.seek(0)

            if allowed_file(medical_receipts.filename):
                filename = secure_filename(medical_receipts.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                medical_receipts.save(file_path)
                saved_files['medical_receipts'] = filename
            else:
                flash("Invalid file type for medical receipt.", "danger")
                return redirect(url_for('route.specific_info', token=token))

            claim = Claim_specific_info(
                user_id=current_user.id,
                first_name=current_user.first_name,
                email=current_user.email,
                hospital_name=hospital_name,
                location=location,
                medical_receipts=saved_files.get('medical_receipts')
            )

            db.session.add(claim)
            db.session.commit()

            claim_num = "CLM" + str(random.randint(10000, 999999))
            while ClaimID.query.filter_by(claim_num=claim_num).first():
                claim_num = "CLM" + str(random.randint(10000, 999999))

            general_info = Claim_general_info.query.filter_by(email=current_user.email).order_by(Claim_general_info.id.desc()).first()

            claim_meta = ClaimID(user_id=current_user.id, first_name=current_user.first_name, email=current_user.email, claim_num=claim_num, specific_info=claim, general_info=general_info)

            db.session.add(claim_meta)
            db.session.commit()

            new_token = current_app.serializer.dumps({'policy_num': policy_num_token})
            return redirect(url_for('route.claim_confirmation', token=new_token))

    return render_template("Login-home/Claim_Specific_Info.html", current_user=current_user, token=policy_num_token)


@route.route('/claims/confirmation', methods=['GET'])
@login_required
def claim_confirmation():
    general_info = Claim_general_info.query.filter_by(email=current_user.email).order_by(Claim_general_info.id.desc()).first()
    specific_info = Claim_specific_info.query.filter_by(email=current_user.email).order_by(Claim_specific_info.id.desc()).first()
    claim_meta = ClaimID.query.filter_by(email=current_user.email).order_by(ClaimID.id.desc()).first()

    return render_template("login-Home/Claim_Confirmation.html", current_user=current_user, general_info=general_info, specific_info=specific_info, claim_meta=claim_meta)


@route.route('/claims_info', methods=['GET'])
@login_required
def claim_info():
    claims = db.session.query(ClaimID, Claim_general_info).join(Claim_general_info, Claim_general_info.id == ClaimID.general_id).filter(ClaimID.email == current_user.email).all()
    claim_lists = []

    for claim, general_info in claims:

        token = current_app.serializer.dumps({'claim_num': claim.claim_num})

        claim_lists.append({
            "claim": claim,
            "general_info": general_info,
            "token": token
        })

    return render_template("user/Claim_Info_list.html", current_user=current_user, claim_lists=claim_lists)


@route.route('/specific_claims_info/<string:token>', methods=['GET'])
@login_required
def specific_claim_info(token):
    try:
        data2 = current_app.serializer.loads(token)
        claim_num = data2['claim_num']
    except Exception:
        abort(400, "Invalid or expired token.")

    claim = ClaimID.query.filter_by(claim_num=claim_num, email=current_user.email).first()
    claim_general = Claim_general_info.query.filter_by(id=ClaimID.general_id).first()
    claim_specific = Claim_specific_info.query.filter_by(id=ClaimID.specific_id).first()

    return render_template("user/Claim_Info.html", claim=claim, claim_general=claim_general, claim_specific=claim_specific, token=token)


@route.route('/security_features/<path:filename>')
def serve_security_file(filename):
    return send_from_directory('Security_Features_Function', filename)
