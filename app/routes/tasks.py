from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import Task, Category, User
from .. import db
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("/", methods=["GET"])
@login_required
def view_tasks():
    # categories summary
    cats = Category.query.all()
    # tasks for current user
    tasks = Task.query.filter_by(owner=current_user).order_by(Task.created_at.desc()).all()
    today_str = datetime.utcnow().strftime("%d %b")
    return render_template("tasks.html", categories=cats, tasks=tasks, today=today_str)

@tasks_bp.route("/add", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category_id = request.form.get("category_id")
    if not title:
        flash("Task title cannot be empty.", "danger")
    else:
        task = Task(title=title, description=description, owner=current_user)
        if category_id:
            cat = Category.query.get(int(category_id))
            if cat:
                task.category = cat
        db.session.add(task)
        db.session.commit()
        flash("Task added.", "success")
    return redirect(url_for("tasks.view_tasks"))

@tasks_bp.route("/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.owner != current_user:
        flash("Not authorized.", "danger")
        return redirect(url_for("tasks.view_tasks"))
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("tasks.view_tasks"))

@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.owner != current_user:
        flash("Not authorized.", "danger")
    else:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted.", "success")
    return redirect(url_for("tasks.view_tasks"))

@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.owner != current_user:
        flash("Not authorized.", "danger")
        return redirect(url_for("tasks.view_tasks"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id")
        if not title:
            flash("Title cannot be empty.", "danger")
            return redirect(url_for("tasks.view_tasks"))
        task.title = title
        task.description = description
        if category_id:
            cat = Category.query.get(int(category_id))
            task.category = cat
        db.session.commit()
        flash("Task updated.", "success")
        return redirect(url_for("tasks.view_tasks"))

    cats = Category.query.all()
    return render_template("tasks.html", categories=cats, tasks=Task.query.filter_by(owner=current_user).all(), editing_task=task)
