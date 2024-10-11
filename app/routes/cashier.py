from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.forms import BillingForm
from app.models import Queue

bp = Blueprint('cashier', __name__)

@bp.route('/')
@bp.route('/cashier')
@login_required
def cashier_dashboard():
    if current_user.role != 'cashier':
        return redirect(url_for('routes.index'))
    billing_queue = db.session.query(Queue).filter(Queue.status == 'billing').order_by(Queue.position).all()

    # Create form instance
    form = BillingForm()
    form.billing_queue.choices = [(q.id, str(q.id)) for q in billing_queue]

    if form.validate_on_submit():
        selected_id = form.billing_queue.data
        # Add logic here for what happens when a billing queue ID is selected and submitted
        flash(f"Selected Queue ID: {selected_id}", "success")
        return redirect(url_for('routes.index'))
    return render_template('cashier/dashboard.html', title='Cashier Dashboard', form=form)
