import os
from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Member, Report

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/emergency', methods=['GET', 'POST'])
def emergency():
    if 'user_id' not in session:
        return redirect('/login')

    user = db.session.get(Member, session['user_id'])

    if request.method == 'POST':
        desc = request.form['description']
        file = request.files.get('photo')
        filename = ''

        if file and file.filename:
            filename = secure_filename(datetime.now().strftime('%Y%m%d_%H%M%S_') + file.filename)
            file.save(os.path.join(UPLOAD_DIR, filename))

        report = Report(
            member_id=user.id,
            description=desc,
            photo_filename=filename
        )
        db.session.add(report)
        db.session.commit()
        flash('✅ 通報已送出')
        return redirect('/emergency')

    return render_template('emergency.html', user=user)
