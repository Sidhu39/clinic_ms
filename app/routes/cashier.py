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
    billing_queue = Queue.query.filter(Queue.status=='billing')
    return render_template('cashier/dashboard.html', title='Cashier Dashboard', billing_queue=billing_queue,cashier_name=current_user.username)
