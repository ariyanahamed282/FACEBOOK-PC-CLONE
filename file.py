import os
import sys
import secrets
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# PART 1: UI TEMPLATES
# ==========================================

FILES = {
    'templates/base.html': '''
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CryptoPro | NextGen</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #6366f1; --secondary: #ec4899; --dark: #0f172a; --card: #1e293b; --text: #f8fafc; }
        body { background-color: var(--dark); color: var(--text); font-family: 'Outfit', sans-serif; padding-bottom: 80px; overflow-x: hidden; }
        .fade-in { animation: fadeIn 0.5s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .navbar-top { background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .navbar-bottom { position: fixed; bottom: 0; width: 100%; background: #1e293b; z-index: 1000; border-top: 1px solid #334155; padding: 10px 0; border-radius: 20px 20px 0 0; box-shadow: 0 -5px 20px rgba(0,0,0,0.5); }

        .nav-link { color: #94a3b8; font-size: 0.75rem; text-align: center; transition: 0.3s; padding: 5px 0; }
        .nav-link:hover, .nav-link.active { color: var(--secondary); transform: translateY(-3px); }
        .nav-icon { font-size: 1.4rem; display: block; margin-bottom: 2px; }

        .card { background: var(--card); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; margin-bottom: 15px; }
        .btn-primary { background: linear-gradient(135deg, var(--primary), var(--secondary)); border: none; font-weight: 600; }

        .sidebar { height: 100%; width: 280px; position: fixed; z-index: 1055; top: 0; left: -280px; background: #1e293b; transition: 0.3s; box-shadow: 10px 0 30px rgba(0,0,0,0.5); }
        .sidebar.active { left: 0; }
        .sidebar-overlay { display: none; position: fixed; width: 100%; height: 100%; top: 0; left: 0; background: rgba(0,0,0,0.8); z-index: 1050; backdrop-filter: blur(3px); }
        .sidebar-link { padding: 15px 25px; color: #cbd5e1; display: block; text-decoration: none; border-left: 3px solid transparent; transition: 0.2s; }
        .sidebar-link:hover { background: rgba(255,255,255,0.05); border-left-color: var(--secondary); color: white; }

        .pay-card { border: 2px solid #334155; transition: 0.3s; cursor: pointer; text-align: center; background: #0f172a; padding: 15px; border-radius: 15px; height: 100%; }
        .pay-card:hover { border-color: var(--primary); transform: translateY(-2px); }
        .pay-card.selected { border-color: #10b981; background: rgba(16, 185, 129, 0.1); }
        .pay-logo { width: 50px; height: 50px; object-fit: contain; margin-bottom: 8px; border-radius: 8px; background: white; padding: 4px; }

        .cp-logo { width: 50px; height: 50px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; transform: rotate(45deg); margin: 0 auto 10px; }
        .cp-logo span { transform: rotate(-45deg); }
        .notif-dot { position: absolute; top: 5px; right: 5px; width: 10px; height: 10px; background: red; border-radius: 50%; border: 2px solid #1e293b; }

        /* SweetAlert Dark Fix */
        div:where(.swal2-container) div:where(.swal2-popup) { background: #1e293b !important; color: #f8fafc !important; border: 1px solid #334155; }
    </style>
</head>
<body>
    {% if current_user.is_authenticated %}
    <nav class="navbar navbar-dark navbar-top sticky-top mb-3">
        <div class="container d-flex justify-content-between align-items-center">
            <button class="btn btn-link text-white p-0" onclick="toggleSidebar()"><i class="fas fa-bars-staggered fa-lg"></i></button>
            <span class="navbar-brand mb-0 h1 fw-bold">Crypto<span style="color: var(--secondary)">Pro</span></span>
            <div class="d-flex align-items-center gap-3">
                <button class="btn btn-link text-white p-0 position-relative" data-bs-toggle="modal" data-bs-target="#notifModal">
                    <i class="fas fa-bell fa-lg"></i>
                    {% if has_unread %}<span class="notif-dot"></span>{% endif %}
                </button>
                <div class="bg-dark px-3 py-1 rounded-pill border border-secondary">
                    <i class="fas fa-wallet text-warning"></i>
                    <span class="fw-bold">${{ "%.2f"|format(current_user.balance) }}</span>
                </div>
            </div>
        </div>
    </nav>
    {% endif %}

    <div class="sidebar-overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="text-center py-5 border-bottom border-secondary bg-gradient-dark">
            <div class="cp-logo"><span>CP</span></div>
            <h5 class="mb-0 text-white fw-bold">{% if current_user.is_authenticated %}{{ current_user.username }}{% else %}Guest{% endif %}</h5>
            {% if current_user.is_authenticated %}
            <div class="mt-2">
                <span class="badge bg-{{ 'success' if current_user.kyc_status == 'Verified' else 'warning' if current_user.kyc_status == 'Pending' else 'danger' }}">
                    {{ current_user.kyc_status }}
                </span>
            </div>
            {% endif %}
        </div>
        <div class="py-3">
            {% if current_user.is_authenticated %}
            <a href="{{ url_for('dashboard') }}" class="sidebar-link"><i class="fas fa-chart-pie me-2"></i> Dashboard</a>
            <a href="{{ url_for('packages') }}" class="sidebar-link"><i class="fas fa-rocket me-2"></i> Invest Plans</a>
            <a href="{{ url_for('active_packages') }}" class="sidebar-link"><i class="fas fa-box-open me-2"></i> My Investments</a>
            <a href="{{ url_for('wallet') }}" class="sidebar-link"><i class="fas fa-wallet me-2"></i> Wallet</a>
            <a href="{{ url_for('refer') }}" class="sidebar-link"><i class="fas fa-users me-2"></i> Referral</a>
            <a href="{{ url_for('page_rules') }}" class="sidebar-link"><i class="fas fa-book me-2"></i> Rules</a>
            <a href="{{ url_for('page_contact') }}" class="sidebar-link"><i class="fas fa-headset me-2"></i> Contact Support</a>
            <a href="{{ url_for('logout') }}" class="sidebar-link text-danger mt-4"><i class="fas fa-sign-out-alt me-2"></i> Logout</a>
            {% else %}
            <a href="{{ url_for('login') }}" class="sidebar-link">Login</a>
            <a href="{{ url_for('register') }}" class="sidebar-link">Register</a>
            {% endif %}
        </div>
    </div>

    <div class="container fade-in">
        {% block content %}{% endblock %}
    </div>

    <!-- Notification Modal -->
    <div class="modal fade" id="notifModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content" style="background:#1e293b; border:1px solid #475569;">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title">Notifications</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-0">
                    <div class="list-group list-group-flush">
                        {% for n in notifications %}
                        <div class="list-group-item bg-transparent text-white border-secondary">
                            <p class="mb-1 small">{{ n.message }}</p>
                            <small class="text-muted" style="font-size:0.65rem">{{ n.timestamp.strftime('%d %b %H:%M') }}</small>
                        </div>
                        {% else %}
                        <div class="p-4 text-center text-muted">No new messages</div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    {% if current_user.is_authenticated %}
    <div class="navbar-bottom">
        <div class="container">
            <div class="row gx-0">
                <div class="col text-center"><a href="{{ url_for('dashboard') }}" class="nav-link {% if request.endpoint == 'dashboard' %}active{% endif %}"><i class="fas fa-home nav-icon"></i> Home</a></div>
                <div class="col text-center"><a href="{{ url_for('packages') }}" class="nav-link {% if request.endpoint == 'packages' %}active{% endif %}"><i class="fas fa-rocket nav-icon"></i> Invest</a></div>
                <div class="col text-center"><a href="{{ url_for('active_packages') }}" class="nav-link {% if request.endpoint == 'active_packages' %}active{% endif %}"><i class="fas fa-layer-group nav-icon"></i> Active</a></div>
                <div class="col text-center"><a href="{{ url_for('wallet') }}" class="nav-link {% if request.endpoint == 'wallet' %}active{% endif %}"><i class="fas fa-wallet nav-icon"></i> Wallet</a></div>
                <div class="col text-center"><a href="{{ url_for('profile') }}" class="nav-link {% if request.endpoint == 'profile' %}active{% endif %}"><i class="fas fa-user-circle nav-icon"></i> Profile</a></div>
            </div>
        </div>
    </div>
    {% endif %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script>
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
            let overlay = document.getElementById('overlay');
            overlay.style.display = overlay.style.display === 'block' ? 'none' : 'block';
        }

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    Swal.fire({
                        icon: '{{ "success" if category == "success" else "error" if category == "danger" else "info" }}',
                        title: '{{ message }}',
                        toast: true, position: 'top-end', showConfirmButton: false, timer: 3000,
                        background: '#1e293b', color: '#fff'
                    });
                {% endfor %}
            {% endif %}
        {% endwith %}

        function confirmAction(url, text) {
            Swal.fire({
                title: 'Are you sure?', text: text, icon: 'warning', showCancelButton: true,
                confirmButtonColor: '#6366f1', cancelButtonColor: '#d33', confirmButtonText: 'Yes',
                background: '#1e293b', color: '#fff'
            }).then((result) => { if (result.isConfirmed) window.location.href = url; })
        }
    </script>
</body>
</html>
    ''',

    # --- DEPOSIT PAGE ---
    'templates/deposit.html': '''
{% extends "base.html" %}
{% block content %}
<h3 class="mt-3">Add Funds</h3>
<div class="alert alert-info small"><i class="fas fa-info-circle"></i> Minimum Deposit: <strong>${{ config.min_deposit }}</strong></div>

<form method="POST">
    <input type="hidden" name="method_id" id="selectedMethod">
    <p class="text-muted small mb-2">SELECT PAYMENT METHOD</p>
    <div class="row g-2 mb-4">
        {% for m in methods %}
        <div class="col-4">
            <div class="pay-card" onclick="selectMethod(this, '{{ m.id }}', '{{ m.rate }}', '{{ m.currency }}', '{{ m.details }}')">
                <img src="{{ m.logo_url }}" class="pay-logo">
                <div class="small fw-bold">{{ m.name }}</div>
                <div class="small text-muted" style="font-size:0.6rem">{{ m.currency }}</div>
            </div>
        </div>
        {% endfor %}
    </div>

    <div class="card p-3 shadow-lg d-none" id="payDetails">
        <div class="alert alert-dark small">
            <div class="d-flex justify-content-between"><span>Rate:</span><span class="text-warning">1 USD = <span id="rate"></span> <span id="curr"></span></span></div>
            <hr class="my-1 border-secondary">
            <div class="mt-2 text-center"><small>Send To:</small><br><div class="bg-black p-2 rounded text-white font-monospace mt-1 user-select-all" id="accDetails"></div></div>
        </div>
        <div class="mb-3"><label>Amount ($ USD)</label><input type="number" step="any" name="amount" class="form-control" id="amt" onkeyup="calc()" required><div class="text-end text-success mt-1 small fw-bold">Pay: <span id="payAmt">0</span> <span id="payCurr"></span></div></div>
        <div class="mb-3"><label>Transaction ID</label><input name="transaction_id" class="form-control" placeholder="Enter TrxID" required></div>
        <button class="btn btn-success w-100 py-3 fw-bold rounded-pill">CONFIRM</button>
    </div>
</form>
<script>
let currentRate=0;
function selectMethod(el,id,rate,curr,details){
    document.querySelectorAll('.pay-card').forEach(c=>c.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('selectedMethod').value=id;
    document.getElementById('payDetails').classList.remove('d-none');
    document.getElementById('rate').innerText=rate;
    document.getElementById('curr').innerText=curr;
    document.getElementById('payCurr').innerText=curr;
    document.getElementById('accDetails').innerText=details;
    currentRate=rate; calc();
}
function calc(){let a=document.getElementById('amt').value;document.getElementById('payAmt').innerText=(a*currentRate).toLocaleString(undefined,{minimumFractionDigits:2});}
</script>
{% endblock %}
    ''',

    # --- WITHDRAW PAGE ---
    'templates/withdraw.html': '''
{% extends "base.html" %}
{% block content %}
<h3 class="mt-3">Withdraw</h3>
<div class="card bg-danger text-white p-3 mb-3 text-center"><small>Balance</small><h2>${{ "%.2f"|format(current_user.balance) }}</h2></div>
<form method="POST">
    <input type="hidden" name="method_id" id="selectedMethod">
    <p class="text-muted small mb-2">SELECT METHOD</p>
    <div class="row g-2 mb-4">
        {% for m in methods %}
        <div class="col-4">
            <div class="pay-card" onclick="selectMethod(this, '{{ m.name }}', '{{ m.currency }}', '{{ m.rate }}')">
                <img src="{{ m.logo_url }}" class="pay-logo">
                <h6 class="mb-0 small">{{ m.name }}</h6>
            </div>
        </div>
        {% endfor %}
    </div>
    <div class="card p-3 shadow-lg d-none" id="wDetails">
        <div class="mb-3"><label>Account Number</label><input name="details" class="form-control" required></div>
        <div class="mb-3"><label>Amount ($)</label><input type="number" step="any" name="amount" class="form-control" id="amt" onkeyup="calc()" required><div class="text-end text-danger mt-1 small fw-bold">You Get: <span id="getAmt">0</span> <span id="getCurr"></span></div></div>
        <button class="btn btn-danger w-100 py-3 fw-bold rounded-pill">REQUEST</button>
    </div>
</form>
<script>
let wRate=0;
function selectMethod(el,name,curr,rate){
    document.querySelectorAll('.pay-card').forEach(c=>c.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('selectedMethod').value=name;
    document.getElementById('wDetails').classList.remove('d-none');
    document.getElementById('getCurr').innerText=curr;
    wRate=rate; calc();
}
function calc(){let a=document.getElementById('amt').value;document.getElementById('getAmt').innerText=(a*wRate).toLocaleString(undefined,{minimumFractionDigits:2});}
</script>
{% endblock %}
    ''',

    # --- ADMIN (FIXED LOGO INPUT) ---
    'templates/admin.html': '''
{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between mt-3 align-items-center"><h2>Admin</h2><a href="{{ url_for('admin_logout') }}" class="btn btn-sm btn-outline-danger">Exit</a></div>
<ul class="nav nav-pills mb-3 nav-fill gap-2 mt-3" id="adminTabs" role="tablist">
    <li class="nav-item"><a class="nav-link active bg-dark border-secondary" data-bs-toggle="tab" href="#fin">Finance</a></li>
    <li class="nav-item"><a class="nav-link bg-dark border-secondary" data-bs-toggle="tab" href="#users">Users</a></li>
    <li class="nav-item"><a class="nav-link bg-dark border-secondary" data-bs-toggle="tab" href="#methods">Methods</a></li>
    <li class="nav-item"><a class="nav-link bg-dark border-secondary" data-bs-toggle="tab" href="#pkg">Plans</a></li>
    <li class="nav-item"><a class="nav-link bg-dark border-secondary" data-bs-toggle="tab" href="#sys">Settings</a></li>
</ul>
<div class="tab-content">
    <!-- FINANCE -->
    <div class="tab-pane fade show active" id="fin">
        <h6 class="text-success">Pending Deposits</h6>
        <div class="table-responsive mb-4"><table class="table table-dark table-sm">{% for d in deposits %}<tr><td>{{ d.user.username }}<br>${{ d.amount }}</td><td>{{ d.method }}<br><small>{{ d.transaction_id }}</small></td><td><form action="{{ url_for('admin_approve_deposit',did=d.id) }}" method="post" class="d-inline"><button class="btn btn-sm btn-success">✓</button></form><a href="#" onclick="confirmAction('{{ url_for('admin_delete_deposit',did=d.id) }}', 'Reject?')" class="btn btn-sm btn-danger">X</a></td></tr>{% else %}<tr><td colspan="3" class="text-center text-muted">No deposits</td></tr>{% endfor %}</table></div>
        <h6 class="text-danger">Pending Withdrawals</h6>
        <div class="table-responsive"><table class="table table-dark table-sm">{% for w in withdrawals %}<tr><td>{{ w.user.username }}<br>${{ w.amount }}</td><td>{{ w.details }}</td><td><form action="{{ url_for('admin_approve_withdraw',wid=w.id) }}" method="post" class="d-inline"><button class="btn btn-sm btn-success">Pay</button></form><form action="{{ url_for('admin_reject_withdraw',wid=w.id) }}" method="post" class="d-inline"><button class="btn btn-sm btn-danger">Rej</button></form></td></tr>{% else %}<tr><td colspan="3" class="text-center text-muted">No withdrawals</td></tr>{% endfor %}</table></div>
    </div>

    <!-- USERS -->
    <div class="tab-pane fade" id="users">
        <div class="table-responsive"><table class="table table-dark table-sm"><thead><tr><th>User</th><th>Bal</th><th>Action</th></tr></thead>{% for u in users %}<tr><td>{{ u.username }}</td><td>${{ "%.1f"|format(u.balance) }}</td><td><form action="{{ url_for('admin_update_user', uid=u.id) }}" method="POST" class="d-flex gap-1"><input type="number" step="0.01" name="new_balance" class="form-control form-control-sm" style="width:60px" placeholder="$$"><button class="btn btn-sm btn-primary"><i class="fas fa-save"></i></button><a href="#" onclick="confirmAction('{{ url_for('admin_delete_user', uid=u.id) }}', 'Delete?')" class="btn btn-sm btn-danger"><i class="fas fa-trash"></i></a></form></td></tr>{% endfor %}</table></div>
    </div>

    <!-- METHODS (FIXED) -->
    <div class="tab-pane fade" id="methods">
        <div class="card p-3 mb-3 border-warning">
            <h6>Add Method</h6>
            <form action="{{ url_for('admin_add_method') }}" method="POST">
                <div class="row g-2 mb-2"><div class="col-6"><select name="type" class="form-select"><option value="deposit">Deposit</option><option value="withdraw">Withdraw</option></select></div><div class="col-6"><input name="currency" class="form-control" placeholder="Currency" required></div></div>
                <div class="row g-2 mb-2"><div class="col-6"><input name="name" class="form-control" placeholder="Name" required></div><div class="col-6"><input type="number" step="any" name="rate" class="form-control" placeholder="Rate" required></div></div>
                <input name="logo_url" class="form-control mb-2" placeholder="Logo Image URL (Required)" required>
                <input name="details" class="form-control mb-2" placeholder="Details" required>
                <button class="btn btn-warning w-100">Add Method</button>
            </form>
        </div>
        <div class="row g-2">{% for m in methods %}<div class="col-6"><div class="card p-2 bg-dark d-flex flex-row align-items-center"><img src="{{ m.logo_url }}" style="width:35px;height:35px;object-fit:contain;background:white;border-radius:8px;padding:2px" class="me-2"><div class="flex-grow-1" style="font-size:0.75rem;line-height:1.2"><strong>{{ m.name }}</strong> ({{ m.currency }})<br><span class="badge bg-secondary" style="font-size:0.6rem">{{ m.type }}</span></div><a href="#" onclick="confirmAction('{{ url_for('admin_delete_method', mid=m.id) }}', 'Delete?')" class="text-danger ms-1"><i class="fas fa-trash"></i></a></div></div>{% endfor %}</div>
    </div>

    <div class="tab-pane fade" id="pkg"><div class="card p-3 mb-3 border-info"><h6>Add Plan</h6><form action="{{ url_for('admin_add_package') }}" method="POST"><div class="row g-2 mb-2"><div class="col"><input name="name" class="form-control" placeholder="Name" required></div><div class="col"><input name="badge" class="form-control" placeholder="Badge"></div></div><div class="row g-2 mb-2"><div class="col"><input type="number" step="any" name="price" class="form-control" placeholder="Price" required></div><div class="col"><input type="number" step="any" name="daily" class="form-control" placeholder="Daily" required></div></div><div class="row g-2 mb-2"><div class="col"><input type="number" name="days" class="form-control" placeholder="Days" required></div><div class="col"><input type="number" name="stock" class="form-control" placeholder="Stock"></div></div><div class="form-check"><input class="form-check-input" type="checkbox" name="return_capital" id="rc"><label class="form-check-label text-white" for="rc">Capital Back</label></div><button class="btn btn-info w-100 mt-2">Create</button></form></div><div class="list-group">{% for p in packages %}<div class="list-group-item bg-dark d-flex justify-content-between"><span>{{ p.name }} - ${{ p.price }}</span><a href="#" onclick="confirmAction('{{ url_for('admin_delete_package',pid=p.id) }}', 'Delete?')" class="text-danger">Del</a></div>{% endfor %}</div></div>
    <div class="tab-pane fade" id="sys"><div class="card p-3 mb-3"><h6>Settings</h6><form action="{{ url_for('admin_update_settings') }}" method="POST"><div class="row g-2 mb-2"><div class="col"><label>Min Dep</label><input name="min_dep" value="{{ config.min_deposit }}" class="form-control"></div><div class="col"><label>Min Wd</label><input name="min_wd" value="{{ config.min_withdraw }}" class="form-control"></div></div><label>Referral %</label><input name="ref_com" value="{{ config.referral_commission }}" class="form-control mb-2"><button class="btn btn-primary w-100">Update</button></form></div><div class="card p-3 mb-3"><h6>Notification</h6><form action="{{ url_for('admin_send_notif') }}" method="POST"><textarea name="message" class="form-control mb-2" placeholder="Message..." required></textarea><button class="btn btn-warning w-100">Broadcast</button></form></div><div class="card p-3"><h6>Pages</h6><form action="{{ url_for('admin_update_content') }}" method="POST"><label>Rules</label><textarea name="rules" class="form-control mb-2" rows="3">{{ config.rules_text }}</textarea><label>Contact</label><textarea name="contact" class="form-control mb-2" rows="3">{{ config.contact_text }}</textarea><button class="btn btn-info w-100">Update</button></form></div></div>
</div>
{% endblock %}
    ''',

    # Keeping others standard
    'templates/register.html': '''{% extends "base.html" %}{% block content %}<div class="row justify-content-center min-vh-100 align-items-center py-5"><div class="col-md-5 col-lg-4"><div class="text-center mb-4"><div class="cp-logo"><span>CP</span></div></div><div class="card p-4 border-0 shadow-lg"><h3 class="text-center fw-bold mb-1">Create Account</h3><p class="text-center text-muted mb-4">Join CryptoPro</p><form method="POST"><div class="mb-3"><label class="small text-muted">USERNAME</label><input type="text" name="username" class="form-control" required></div><div class="mb-3"><label class="small text-muted">EMAIL</label><input type="email" name="email" class="form-control" placeholder="example@mail.com" required></div><div class="mb-3"><label class="small text-muted">PASSWORD</label><input type="password" name="password" id="p" class="form-control" onkeyup="chk()" required><div class="progress mt-1" style="height:3px"><div class="progress-bar" id="pb" style="width:0%"></div></div><small id="pt" class="text-muted" style="font-size:0.7rem">Strength</small></div><div class="mb-3"><label class="small text-muted">CONFIRM PASSWORD</label><input type="password" name="confirm" class="form-control" required></div><div class="mb-3"><label class="small text-muted">REFERRAL (Optional)</label><input type="text" name="referral_code" class="form-control" value="{{ request.args.get('ref', '') }}"></div><div class="mb-4"><label class="small text-muted">MATH: {{ captcha_q }} = ?</label><input type="number" name="captcha" class="form-control text-center text-warning fw-bold" required></div><button class="btn btn-primary w-100 py-3 rounded-pill">REGISTER</button></form><div class="text-center mt-4"><a href="{{ url_for('login') }}" class="text-decoration-none text-light small">Back to Login</a></div></div></div></div><script>function chk(){let v=document.getElementById('p').value,b=document.getElementById('pb'),t=document.getElementById('pt'),s=0;if(v.length>5)s+=30; if(v.match(/[0-9]/))s+=35; if(v.match(/[^A-Za-z0-9]/))s+=35;b.style.width=s+'%';if(s<40){b.className='progress-bar bg-danger';t.innerText='Weak';}else if(s<80){b.className='progress-bar bg-warning';t.innerText='Medium';}else{b.className='progress-bar bg-success';t.innerText='Strong';}}</script>{% endblock %}''',
    'templates/login.html': '''{% extends "base.html" %}{% block content %}<div class="row justify-content-center min-vh-100 align-items-center py-5"><div class="col-md-5 col-lg-4"><div class="text-center mb-4"><div class="cp-logo"><span>CP</span></div></div><div class="card p-4 border-0 shadow-lg"><h3 class="text-center fw-bold">Login</h3><p class="text-center text-muted mb-4">Welcome Back</p><form method="POST"><div class="mb-3"><label class="small text-muted">USERNAME / EMAIL</label><input type="text" name="login_id" class="form-control" required></div><div class="mb-3"><label class="small text-muted">PASSWORD</label><input type="password" name="password" class="form-control" required></div><div class="mb-4"><label class="small text-muted">MATH: {{ captcha_q }} = ?</label><input type="number" name="captcha" class="form-control text-center text-warning fw-bold" required></div><button class="btn btn-primary w-100 py-3 rounded-pill">LOGIN</button></form><div class="text-center mt-4"><a href="{{ url_for('register') }}" class="text-decoration-none text-light small">Create Account</a></div></div></div></div>{% endblock %}''',
    'templates/dashboard.html': '''{% extends "base.html" %}{% block content %}<div class="card p-0 overflow-hidden mb-3 mt-3 shadow"><div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{"symbols":[{"proName":"BITSTAMP:BTCUSD","title":"Bitcoin"},{"proName":"BITSTAMP:ETHUSD","title":"Ethereum"},{"proName":"BINANCE:BNBUSDT","title":"BNB"}],"colorTheme":"dark","isTransparent":false,"displayMode":"adaptive","locale":"en"}</script></div></div><div class="card bg-gradient-dark p-4 text-center border-0" style="background:linear-gradient(135deg,#1e293b,#0f172a)"><small class="text-muted">Total Balance</small><h1 class="display-4 fw-bold text-white mb-0">${{ "%.2f"|format(current_user.balance) }}</h1><div class="mt-2"><span class="badge bg-dark border border-secondary">≈ {{ "%.2f"|format(current_user.balance*140) }} BDT</span></div></div><div class="row g-2 mb-3"><div class="col-6"><a href="{{ url_for('deposit') }}" class="btn btn-success w-100 py-3 rounded-4"><i class="fas fa-arrow-down"></i> Deposit</a></div><div class="col-6"><a href="{{ url_for('withdraw') }}" class="btn btn-danger w-100 py-3 rounded-4"><i class="fas fa-arrow-up"></i> Withdraw</a></div></div><h5 class="mb-3 text-white">Live Market</h5><div class="card p-0 overflow-hidden" style="height:400px"><div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>{"colorTheme":"dark","dateRange":"12M","showChart":true,"locale":"en","width":"100%","height":"100%","isTransparent":true,"tabs":[{"title":"Crypto","symbols":[{"s":"BINANCE:BTCUSDT"},{"s":"BINANCE:ETHUSDT"},{"s":"BINANCE:SOLUSDT"}]}]}</script></div></div>{% endblock %}''',
    'templates/wallet.html': '''{% extends "base.html" %}{% block content %}<div class="card bg-dark p-4 text-center border-primary mt-3 shadow-lg"><small class="text-muted">Available Funds</small><h2 class="fw-bold text-white mb-0">${{ "%.2f"|format(current_user.balance) }}</h2></div><div class="row g-2 mb-4"><div class="col-6"><a href="{{ url_for('deposit') }}" class="btn btn-success w-100 py-3 rounded-4 shadow"><i class="fas fa-arrow-down mb-1"></i><br>Deposit</a></div><div class="col-6"><a href="{{ url_for('withdraw') }}" class="btn btn-danger w-100 py-3 rounded-4 shadow"><i class="fas fa-arrow-up mb-1"></i><br>Withdraw</a></div></div><h5 class="mb-3 border-bottom pb-2 border-secondary">Transaction History</h5><div class="list-group">{% for t in history %}<div class="list-group-item bg-dark border-secondary text-white rounded-3 mb-2"><div class="d-flex justify-content-between align-items-center"><div>{% if t.status == 'Pending' %}<span class="text-warning fw-bold"><i class="fas fa-clock"></i> {{ t.desc }}</span>{% else %}<span class="fw-bold text-truncate" style="max-width: 180px;">{{ t.desc }}</span>{% endif %}<br><small class="text-muted">{{ t.date }}</small></div><div class="text-end"><span class="{{ 'text-success' if t.amt > 0 else 'text-danger' }} fw-bold fs-5">{{ '+' if t.amt > 0 else '' }}{{ "%.2f"|format(t.amt) }}</span><br><span class="badge {{ 'bg-warning' if t.status=='Pending' else 'bg-secondary' }}" style="font-size: 0.6rem">{{ t.status }}</span></div></div></div>{% else %}<div class="text-center py-5 text-muted">No history found</div>{% endfor %}</div>{% endblock %}''',
    'templates/packages.html': '''{% extends "base.html" %}{% block content %}<h3 class="mt-3 text-center">Plans</h3><div class="row">{% for p in packages %}<div class="col-md-6"><div class="card p-4 text-center border-primary shadow-lg position-relative overflow-hidden"><div class="position-absolute top-0 end-0 bg-primary text-white px-3 py-1 small rounded-bottom-start">VIP {{ loop.index }}</div><h4 class="text-primary fw-bold">{{ p.name }}</h4><h1 class="my-3">${{ p.price }}</h1><ul class="list-group list-group-flush small bg-transparent text-start mb-3"><li class="list-group-item bg-transparent text-white"><i class="fas fa-check text-success me-2"></i> Daily: ${{ p.daily_income }}</li><li class="list-group-item bg-transparent text-white"><i class="fas fa-clock text-info me-2"></i> {{ p.duration }} Days</li><li class="list-group-item bg-transparent text-white"><i class="fas fa-chart-line text-warning me-2"></i> Total: ${{ p.daily_income * p.duration }}</li></ul><form action="{{ url_for('buy_package',pid=p.id) }}" method="post" onsubmit="return confirm('Purchase {{ p.name }} for ${{ p.price }}?')"><button class="btn btn-outline-primary w-100 rounded-pill fw-bold">Invest Now</button></form></div></div>{% else %}<div class="text-center py-5">No plans available</div>{% endfor %}</div>{% endblock %}''',
    'templates/active_packages.html': '''{% extends "base.html" %}{% block content %}<h3 class="mt-3">My Investments</h3>{% for s in subscriptions %}<div class="card border-start border-4 border-success mb-3 p-3 shadow"><div class="d-flex justify-content-between align-items-center"><div><h5 class="mb-0">{{ s.package_name }}</h5><small class="text-muted">Ends: {{ s.end_date.strftime('%d %b') }}</small></div><div class="text-end"><span class="badge bg-success mb-1">Running</span><br><small>Daily: ${{ s.daily_income }}</small></div></div><hr class="border-secondary"><form action="{{ url_for('claim_package',sid=s.id) }}" method="post">{% if s.can_claim %}<button class="btn btn-success w-100">Claim Profit</button>{% else %}<button class="btn btn-dark w-100" disabled><i class="fas fa-clock"></i> Next: {{ s.time_remaining }}</button>{% endif %}</form></div>{% else %}<div class="text-center py-5 text-muted">No active plans</div>{% endfor %}{% endblock %}''',
    'templates/refer.html': '''{% extends "base.html" %}{% block content %}<div class="card text-center p-4 mt-3 border-warning"><i class="fas fa-gift fa-3x text-warning mb-2"></i><h3>Refer & Earn</h3><p class="text-muted">Earn <span class="text-white fs-5 fw-bold">{{ config.referral_commission }}%</span> Commission</p><div class="input-group mb-3"><input type="text" class="form-control bg-black text-white" value="{{ request.host_url }}register?ref={{ current_user.referral_code }}" id="refLink" readonly><button class="btn btn-warning" onclick="copyRef()"><i class="fas fa-copy"></i></button></div><div class="bg-black p-2 rounded border border-secondary d-inline-block px-4"><small class="text-muted">CODE:</small> <span class="fw-bold text-white ms-2">{{ current_user.referral_code }}</span></div></div><h5 class="mt-4">My Team</h5><ul class="list-group">{% for r in referrals %}<li class="list-group-item bg-dark text-white border-secondary d-flex justify-content-between"><span><i class="fas fa-user-circle"></i> {{ r.username }}</span><span>{{ r.created_at.strftime('%d %b') }}</span></li>{% else %}<li class="list-group-item bg-transparent text-center text-muted">No referrals yet</li>{% endfor %}</ul><script>function copyRef(){let c=document.getElementById("refLink");c.select();navigator.clipboard.writeText(c.value);alert("Link Copied!");}</script>{% endblock %}''',
    'templates/profile.html': '''{% extends "base.html" %}{% block content %}<div class="text-center mt-4 mb-4"><div class="cp-logo"><span>CP</span></div><h4>{{ current_user.username }}</h4><p class="text-muted">{{ current_user.email }}</p><div class="mt-2">{% if current_user.kyc_status == 'Verified' %}<span class="badge bg-success p-2 px-3 rounded-pill"><i class="fas fa-check-circle"></i> Verified Account</span>{% elif current_user.kyc_status == 'Pending' %}<button class="btn btn-warning btn-sm rounded-pill px-3" disabled><i class="fas fa-spinner fa-spin"></i> Pending Verification (Wait 5 min)</button>{% else %}<button class="btn btn-danger btn-sm rounded-pill px-3" data-bs-toggle="modal" data-bs-target="#kycModal"><i class="fas fa-exclamation-circle"></i> Unverified - Click to Verify</button>{% endif %}</div><div class="d-flex justify-content-center gap-3 text-small mt-3"><div class="bg-dark px-3 py-1 rounded border border-secondary">Joined: {{ current_user.created_at.strftime('%Y-%m-%d') }}</div><div class="bg-dark px-3 py-1 rounded border border-secondary">Balance: ${{ "%.2f"|format(current_user.balance) }}</div></div></div>{% if current_user.kyc_status == 'Verified' %}<div class="card p-3 shadow border-success"><h6 class="text-success mb-2"><i class="fas fa-id-card"></i> Personal Info</h6><small class="text-muted">Full Name</small><div class="text-white fw-bold mb-2">{{ current_user.full_name }}</div><small class="text-muted">Country</small><div class="text-white fw-bold mb-2">{{ current_user.country }}</div><small class="text-muted">Phone</small><div class="text-white fw-bold">{{ current_user.phone }}</div></div>{% endif %}<div class="card p-3 shadow"><h5 class="mb-3">Change Password</h5><form action="{{ url_for('change_password') }}" method="POST"><div class="mb-2"><input type="password" name="current_pw" class="form-control" placeholder="Current Password" required></div><div class="mb-2"><input type="password" name="new_pw" class="form-control" placeholder="New Password" required></div><button class="btn btn-primary w-100">Update Password</button></form></div><div class="list-group mt-3"><a href="{{ url_for('logout') }}" class="list-group-item bg-dark text-danger"><i class="fas fa-sign-out-alt w-25"></i> Logout</a></div><!-- KYC MODAL --><div class="modal fade" id="kycModal" tabindex="-1"><div class="modal-dialog modal-dialog-centered"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Account Verification</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div><form action="{{ url_for('submit_kyc') }}" method="POST"><div class="modal-body"><div class="alert alert-info small">Fill your real information. Verification takes 5 minutes.</div><div class="mb-3"><label>Full Name</label><input type="text" name="full_name" class="form-control" required></div><div class="mb-3"><label>Country</label><select name="country" class="form-select" required><option value="">Select Country</option><option value="Bangladesh">Bangladesh</option><option value="India">India</option><option value="Pakistan">Pakistan</option><option value="USA">USA</option><option value="UK">UK</option><option value="Other">Other</option></select></div><div class="mb-3"><label>Phone Number (with Code)</label><input type="text" name="phone" class="form-control" placeholder="+880..." required></div></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button><button type="submit" class="btn btn-primary">Submit Verification</button></div></form></div></div></div>{% endblock %}''',
    'templates/page_rules.html': '''{% extends "base.html" %}{% block content %}<h3 class="mt-3">Platform Rules</h3><div class="card p-4"><div class="text-white" style="white-space: pre-wrap;">{{ content }}</div></div>{% endblock %}''',
    'templates/page_contact.html': '''{% extends "base.html" %}{% block content %}<h3 class="mt-3">Contact Support</h3><div class="card p-4"><div class="text-white" style="white-space: pre-wrap;">{{ content }}</div></div>{% endblock %}''',
    'templates/admin_login.html': '''<!DOCTYPE html><html data-bs-theme="dark"><head><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><style>body{background:#000;height:100vh;display:flex;justify-content:center;align-items:center}</style></head><body><div class="card p-4"><h4 class="text-center">Admin</h4><form method="POST"><input type="password" name="pin" class="form-control mb-3 text-center" placeholder="PIN" style="letter-spacing:5px"><button class="btn btn-danger w-100">Unlock</button></form></div></body></html>'''
}

def create_files():
    import shutil
    if os.path.exists('templates'): shutil.rmtree('templates')
    os.makedirs('templates')
    for path, content in FILES.items():
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
create_files()

# ==========================================
# PART 2: FLASK & DB
# ==========================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultra-secure-key-2025'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rewards.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==========================================
# PART 3: MODELS
# ==========================================
class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    min_deposit = db.Column(db.Float, default=5.0)
    min_withdraw = db.Column(db.Float, default=10.0)
    referral_commission = db.Column(db.Float, default=15.0)
    rules_text = db.Column(db.Text, default="1. One account per user.\n2. Do not use VPN.")
    contact_text = db.Column(db.Text, default="Email: support@crypto.pro\nTelegram: @admin")

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    balance = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(10), unique=True)
    referred_by = db.Column(db.Integer, nullable=True)

    # KYC Fields
    full_name = db.Column(db.String(100))
    country = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    kyc_status = db.Column(db.String(20), default='Unverified') # Unverified, Pending, Verified
    kyc_time = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscriptions = db.relationship('UserSubscription', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    deposits = db.relationship('Deposit', backref='user', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='user', lazy=True)

class PackagePlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    daily_income = db.Column(db.Float)
    duration = db.Column(db.Integer)

class UserSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    package_id = db.Column(db.Integer)
    package_name = db.Column(db.String(50))
    daily_income = db.Column(db.Float)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    last_claim = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, default=True)

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    name = db.Column(db.String(30))
    currency = db.Column(db.String(10))
    rate = db.Column(db.Float)
    details = db.Column(db.String(100))
    logo_url = db.Column(db.String(200)) # Logo Support

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    description = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_type = db.Column(db.String(20), default='general') # referral, deposit, withdraw, profit

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    method = db.Column(db.String(50))
    details = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    u = User.query.get(int(user_id))
    # AUTO KYC VERIFY LOGIC (5 Minutes)
    if u and u.kyc_status == 'Pending':
        if datetime.utcnow() > u.kyc_time + timedelta(minutes=5):
            u.kyc_status = 'Verified'
            db.session.commit()
    return u

def get_config():
    conf = SystemSettings.query.first()
    if not conf:
        conf = SystemSettings()
        db.session.add(conf)
        db.session.commit()
    return conf

@app.context_processor
def inject_globals():
    notifications = Notification.query.order_by(Notification.timestamp.desc()).limit(5).all()
    return dict(config=get_config(), notifications=notifications, has_unread=len(notifications)>0)

# ==========================================
# PART 4: ROUTES
# ==========================================
def add_balance(user, amount, desc, type='general'):
    user.balance += amount
    db.session.add(Transaction(user_id=user.id, amount=amount, description=desc, transaction_type=type))
    db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'GET':
        n1, n2 = random.randint(1, 9), random.randint(1, 9)
        session['captcha'] = n1 + n2
        return render_template('login.html', captcha_q=f"{n1} + {n2}")
    if request.method == 'POST':
        if int(request.form.get('captcha',0)) != session.get('captcha',0):
            flash('Captcha Incorrect', 'danger'); return redirect(url_for('login'))
        user = User.query.filter((User.username==request.form.get('login_id'))|(User.email==request.form.get('login_id'))).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid Login', 'danger')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'GET':
        n1, n2 = random.randint(1, 9), random.randint(1, 9)
        session['captcha'] = n1 + n2
        return render_template('register.html', captcha_q=f"{n1} + {n2}")
    if request.method == 'POST':
        if int(request.form.get('captcha',0)) != session.get('captcha',0):
            flash('Captcha Incorrect', 'danger'); return redirect(url_for('register'))
        email = request.form.get('email')
        if '@' not in email: flash('Invalid Email format', 'danger'); return redirect(url_for('register'))
        if request.form.get('password') != request.form.get('confirm'): flash('Passwords do not match', 'danger'); return redirect(url_for('register'))
        if len(request.form.get('password')) < 6: flash('Password too weak (min 6 chars)', 'danger'); return redirect(url_for('register'))
        if User.query.filter_by(username=request.form.get('username')).first(): flash('Username taken', 'warning'); return redirect(url_for('register'))
        hashed = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
        ref_code = secrets.token_hex(4)
        ref_id = None
        if request.form.get('referral_code'):
            referrer = User.query.filter_by(referral_code=request.form.get('referral_code')).first()
            if referrer: ref_id = referrer.id
        user = User(username=request.form.get('username'), email=email, password=hashed, referral_code=ref_code, referred_by=ref_id)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))

@app.route('/')
def index(): return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html')

@app.route('/wallet')
@login_required
def wallet():
    history = []
    for t in Transaction.query.filter_by(user_id=current_user.id).all():
        history.append({'desc': t.description, 'amt': t.amount, 'date': t.timestamp.strftime('%d %b %H:%M'), 'status': 'Completed', 'ts': t.timestamp})
    for d in Deposit.query.filter_by(user_id=current_user.id, status='Pending').all():
        history.append({'desc': f"Deposit ({d.method})", 'amt': d.amount, 'date': d.timestamp.strftime('%d %b %H:%M'), 'status': 'Pending', 'ts': d.timestamp})
    for w in Withdrawal.query.filter_by(user_id=current_user.id, status='Pending').all():
        history.append({'desc': f"Withdraw ({w.method})", 'amt': -w.amount, 'date': w.timestamp.strftime('%d %b %H:%M'), 'status': 'Pending', 'ts': w.timestamp})
    history.sort(key=lambda x: x['ts'], reverse=True)
    return render_template('wallet.html', history=history)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amt = float(request.form.get('amount'))
        conf = get_config()
        if amt < conf.min_deposit: flash(f"Min Deposit is ${conf.min_deposit}", "warning"); return redirect(url_for('deposit'))
        mid = request.form.get('method_id')
        method = PaymentMethod.query.get(mid)
        if not method: return redirect(url_for('deposit'))
        dep = Deposit(user_id=current_user.id, amount=amt, method=f"{method.name} ({method.currency})", transaction_id=request.form.get('transaction_id'))
        db.session.add(dep)
        db.session.commit()
        flash('Submitted!', 'success')
        return redirect(url_for('wallet'))
    methods = PaymentMethod.query.filter_by(type='deposit').all()
    return render_template('deposit.html', methods=methods)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        amt = float(request.form.get('amount'))
        conf = get_config()
        if amt < conf.min_withdraw: flash(f"Min Withdraw is ${conf.min_withdraw}", "warning"); return redirect(url_for('withdraw'))
        if current_user.balance < amt: flash('Insufficient Balance', 'danger')
        else:
            add_balance(current_user, -amt, f"Withdraw Request: ${amt}", 'withdraw')
            wd = Withdrawal(user_id=current_user.id, amount=amt, method=request.form.get('method_id'), details=request.form.get('details'))
            db.session.add(wd); db.session.commit()
            flash('Requested!', 'success')
            return redirect(url_for('wallet'))
    methods = PaymentMethod.query.filter_by(type='withdraw').all()
    return render_template('withdraw.html', methods=methods)

@app.route('/packages')
@login_required
def packages(): return render_template('packages.html', packages=PackagePlan.query.all())

@app.route('/buy_package/<int:pid>', methods=['POST'])
@login_required
def buy_package(pid):
    pkg = PackagePlan.query.get_or_404(pid)
    count = UserSubscription.query.filter_by(user_id=current_user.id, package_id=pid).count()
    if count >= 2: flash("Limit reached (Max 2)", "warning"); return redirect(url_for('packages'))
    if current_user.balance < pkg.price: flash('Insufficient Funds', 'danger'); return redirect(url_for('wallet'))
    add_balance(current_user, -pkg.price, f"Invested: {pkg.name}", 'investment')
    end = datetime.utcnow() + timedelta(days=pkg.duration)
    sub = UserSubscription(user_id=current_user.id, package_id=pkg.id, package_name=pkg.name, daily_income=pkg.daily_income, end_date=end)
    db.session.add(sub); db.session.commit()
    flash('Success!', 'success')
    return redirect(url_for('active_packages'))

@app.route('/active_packages')
@login_required
def active_packages():
    subs = UserSubscription.query.filter_by(user_id=current_user.id, active=True).order_by(UserSubscription.start_date.desc()).all()
    now = datetime.utcnow()
    res = []
    for s in subs:
        if now > s.end_date: s.active = False; db.session.commit(); continue
        can_claim = False; time_rem = ""
        if s.last_claim is None: can_claim = True
        else:
            diff = now - s.last_claim
            if diff >= timedelta(hours=24): can_claim = True
            else:
                rem = timedelta(hours=24) - diff
                h, r = divmod(int(rem.total_seconds()), 3600); m, _ = divmod(r, 60)
                time_rem = f"{h}h {m}m"
        s.can_claim = can_claim; s.time_remaining = time_rem; res.append(s)
    return render_template('active_packages.html', subscriptions=res)

@app.route('/claim_package/<int:sid>', methods=['POST'])
@login_required
def claim_package(sid):
    sub = UserSubscription.query.filter_by(id=sid, user_id=current_user.id, active=True).first_or_404()
    now = datetime.utcnow()
    if sub.last_claim and (now - sub.last_claim) < timedelta(hours=24): return redirect(url_for('active_packages'))
    sub.last_claim = now
    add_balance(current_user, sub.daily_income, f"Profit: {sub.package_name}", 'profit')
    flash(f"Claimed ${sub.daily_income}", 'success')
    return redirect(url_for('active_packages'))

@app.route('/refer')
@login_required
def refer():
    refs = User.query.filter_by(referred_by=current_user.id).all()
    commissions = Transaction.query.filter_by(user_id=current_user.id, transaction_type='referral').order_by(Transaction.timestamp.desc()).all()
    return render_template('refer.html', referrals=refs, commissions=commissions)

@app.route('/submit_kyc', methods=['POST'])
@login_required
def submit_kyc():
    current_user.full_name = request.form.get('full_name')
    current_user.country = request.form.get('country')
    current_user.phone = request.form.get('phone')
    current_user.kyc_status = 'Pending'
    current_user.kyc_time = datetime.utcnow()
    db.session.commit()
    flash('Verification Submitted. Please wait 5 minutes.', 'info')
    return redirect(url_for('profile'))

@app.route('/rules')
def page_rules(): return render_template('page_rules.html', content=get_config().rules_text)

@app.route('/contact')
def page_contact(): return render_template('page_contact.html', content=get_config().contact_text)

@app.route('/profile')
@login_required
def profile(): return render_template('profile.html')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if not check_password_hash(current_user.password, request.form.get('current_pw')): flash('Wrong current password', 'danger')
    else:
        current_user.password = generate_password_hash(request.form.get('new_pw'), method='pbkdf2:sha256')
        db.session.commit()
        flash('Password Updated', 'success')
    return redirect(url_for('profile'))

@app.route('/logout')
def logout(): logout_user(); return redirect(url_for('login'))

# --- ADMIN ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST' and request.form.get('pin') == '1234': session['admin'] = True; return redirect(url_for('admin_panel'))
    if not session.get('admin'): return render_template('admin_login.html')
    return render_template('admin.html', config=get_config(), packages=PackagePlan.query.all(), methods=PaymentMethod.query.all(), deposits=Deposit.query.filter_by(status='Pending').all(), withdrawals=Withdrawal.query.filter_by(status='Pending').all(), users=User.query.all())

@app.route('/admin/logout')
def admin_logout(): session.pop('admin', None); return redirect(url_for('login'))

@app.route('/admin/update_settings', methods=['POST'])
def admin_update_settings():
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    c = get_config()
    c.min_deposit = float(request.form.get('min_dep'))
    c.min_withdraw = float(request.form.get('min_wd'))
    c.referral_commission = float(request.form.get('ref_com'))
    db.session.commit(); flash('Updated', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/update_content', methods=['POST'])
def admin_update_content():
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    c = get_config()
    c.rules_text = request.form.get('rules')
    c.contact_text = request.form.get('contact')
    db.session.commit(); flash('Content Updated', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/send_notif', methods=['POST'])
def admin_send_notif():
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    db.session.add(Notification(message=request.form.get('message')))
    db.session.commit(); flash('Notification Sent', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/approve_deposit/<int:did>', methods=['POST'])
def admin_approve_deposit(did):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    d = Deposit.query.get(did)
    d.status = 'Approved'
    add_balance(d.user, d.amount, f"Deposit Approved: {d.method}", 'deposit')
    if d.user.referred_by:
        ref = User.query.get(d.user.referred_by)
        conf = get_config()
        if ref: add_balance(ref, d.amount * (conf.referral_commission/100), f"Ref Bonus from {d.user.username}", 'referral')
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_deposit/<int:did>')
def admin_delete_deposit(did):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    d = Deposit.query.get(did); db.session.delete(d); db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/approve_withdraw/<int:wid>', methods=['POST'])
def admin_approve_withdraw(wid):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    w = Withdrawal.query.get(wid)
    w.status = 'Paid'
    db.session.add(Transaction(user_id=w.user_id, amount=0, description=f"Withdrawal Paid (${w.amount})", transaction_type='withdraw'))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/reject_withdraw/<int:wid>', methods=['POST'])
def admin_reject_withdraw(wid):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    w = Withdrawal.query.get(wid)
    w.status = 'Rejected'
    add_balance(w.user, w.amount, "Withdrawal Rejected (Refund)", 'withdraw')
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_package', methods=['POST'])
def admin_add_package():
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    db.session.add(PackagePlan(name=request.form['name'], price=float(request.form['price']), daily_income=float(request.form['daily']), duration=int(request.form['days'])))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_package/<int:pid>')
def admin_delete_package(pid):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    db.session.delete(PackagePlan.query.get(pid)); db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_method', methods=['POST'])
def admin_add_method():
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    db.session.add(PaymentMethod(type=request.form['type'], name=request.form['name'], details=request.form['details'], currency=request.form['currency'], rate=float(request.form['rate']), logo_url=request.form.get('logo_url')))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_method/<int:mid>')
def admin_delete_method(mid):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    db.session.delete(PaymentMethod.query.get(mid)); db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/update_user/<int:uid>', methods=['POST'])
def admin_update_user(uid):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    u = User.query.get(uid)
    u.balance = float(request.form['new_balance'])
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_user/<int:uid>')
def admin_delete_user(uid):
    if not session.get('admin'): return redirect(url_for('admin_panel'))
    db.session.delete(User.query.get(uid))
    db.session.commit()
    return redirect(url_for('admin_panel'))

# ==================== INIT ====================
def init_db():
    db.create_all()
    # Add Default Methods if none exist
    if not PaymentMethod.query.first():
        defaults = [
            ('Deposit', 'Bkash Personal', 'BDT', 140, '01700000000', 'https://freelogopng.com/images/all_img/1656234745bkash-app-logo-png.png'),
            ('Deposit', 'Nagad Personal', 'BDT', 140, '01800000000', 'https://freelogopng.com/images/all_img/1679248787Nagad-Logo.png'),
            ('Deposit', 'Binance Pay', 'USDT', 1, 'MyPayID', 'https://cryptologos.cc/logos/binance-coin-bnb-logo.png'),
            ('Deposit', 'USDT (TRC20)', 'USDT', 1, 'Txxxxxxxx', 'https://cryptologos.cc/logos/tether-usdt-logo.png'),
            ('Withdraw', 'Bkash', 'BDT', 140, '', 'https://freelogopng.com/images/all_img/1656234745bkash-app-logo-png.png'),
        ]
        for t, n, c, r, d, l in defaults:
            db.session.add(PaymentMethod(type=t, name=n, currency=c, rate=r, details=d, logo_url=l))
        db.session.commit()
        print("Default methods added.")

if __name__ == "__main__":
    with app.app_context(): init_db()
    app.run(debug=True)
