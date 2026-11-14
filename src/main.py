from datetime import date, datetime
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///roadmap.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Enforce SQLite foreign key constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# --- Database Models ---
class Roadmap(db.Model):
    __tablename__ = "roadmaps"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    color_hex = db.Column(db.String(7), default="#3b82f6")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    stages = db.relationship(
        "Stage",
        backref="roadmap",
        cascade="all, delete-orphan",
        order_by="Stage.position",
        lazy=True,
    )
    projects = db.relationship(
        "Project",
        backref="roadmap",
        cascade="all, delete-orphan",
        order_by="Project.created_at.desc()",
        lazy=True,
    )
    notes = db.relationship(
        "Note",
        backref="roadmap",
        cascade="all, delete-orphan",
        order_by="Note.updated_at.desc()",
        lazy=True,
    )

    @property
    def progress(self) -> int:
        total = sum(len(s.topics) for s in self.stages)
        if total == 0:
            return 0
        completed = sum(
            1 for s in self.stages for t in s.topics if t.status == "completed"
        )
        return round((completed / total) * 100)


class Stage(db.Model):
    __tablename__ = "stages"
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(
        db.Integer, db.ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)

    topics = db.relationship(
        "Topic",
        backref="stage",
        cascade="all, delete-orphan",
        order_by="Topic.position",
        lazy=True,
    )


class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(
        db.Integer, db.ForeignKey("stages.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default="not_started")
    priority = db.Column(db.String(20), default="medium")
    due_date = db.Column(db.Date, nullable=True)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(
        db.Integer, db.ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False
    )
    stage_id = db.Column(
        db.Integer, db.ForeignKey("stages.id", ondelete="SET NULL"), nullable=True
    )
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="planned")
    tech_stack = db.Column(db.String(255))
    repo_url = db.Column(db.String(255))
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    stage = db.relationship("Stage", lazy=True)


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(
        db.Integer, db.ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False
    )
    stage_id = db.Column(
        db.Integer, db.ForeignKey("stages.id", ondelete="CASCADE"), nullable=True
    )
    topic_id = db.Column(
        db.Integer, db.ForeignKey("topics.id", ondelete="CASCADE"), nullable=True
    )
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    stage = db.relationship("Stage", lazy=True)
    topic = db.relationship("Topic", lazy=True)


# --- Helpers ---
def parse_date(date_str: str | None) -> date | None:
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


with app.app_context():
    db.create_all()


# --- Routes ---
@app.route("/")
def index():
    roadmaps = Roadmap.query.order_by(Roadmap.created_at.asc()).all()
    selected_roadmap_id = request.args.get("roadmap_id", type=int)
    selected_roadmap = (
        db.session.get(Roadmap, selected_roadmap_id)
        if selected_roadmap_id
        else (roadmaps[0] if roadmaps else None)
    )
    return render_template(
        "index.html", roadmaps=roadmaps, selected_roadmap=selected_roadmap
    )


# --- Roadmap Routes ---
@app.route("/roadmap/create", methods=["POST"])
def create_roadmap():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    color = request.form.get("color_hex", "#3b82f6")
    if title:
        roadmap = Roadmap(title=title, description=description, color_hex=color)
        db.session.add(roadmap)
        db.session.commit()
        return redirect(url_for("index", roadmap_id=roadmap.id))
    return redirect(url_for("index"))


@app.route("/roadmap/<int:roadmap_id>/edit", methods=["POST"])
def edit_roadmap(roadmap_id: int):
    roadmap = db.get_or_404(Roadmap, roadmap_id)
    title = request.form.get("title", "").strip()
    if title:
        roadmap.title = title
        roadmap.description = request.form.get("description", "").strip()
        roadmap.color_hex = request.form.get("color_hex", roadmap.color_hex)
        db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap.id))


@app.route("/roadmap/<int:roadmap_id>/delete", methods=["POST"])
def delete_roadmap(roadmap_id: int):
    roadmap = db.get_or_404(Roadmap, roadmap_id)
    db.session.delete(roadmap)
    db.session.commit()
    return redirect(url_for("index"))


# --- Stage Routes ---
@app.route("/roadmap/<int:roadmap_id>/stage/create", methods=["POST"])
def create_stage(roadmap_id: int):
    roadmap = db.get_or_404(Roadmap, roadmap_id)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if title:
        stage = Stage(
            roadmap_id=roadmap.id,
            title=title,
            description=description,
            position=len(roadmap.stages),
        )
        db.session.add(stage)
        db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap.id))


@app.route("/stage/<int:stage_id>/edit", methods=["POST"])
def edit_stage(stage_id: int):
    stage = db.get_or_404(Stage, stage_id)
    title = request.form.get("title", "").strip()
    if title:
        stage.title = title
        stage.description = request.form.get("description", "").strip()
        db.session.commit()
    return redirect(url_for("index", roadmap_id=stage.roadmap_id))


@app.route("/stage/<int:stage_id>/delete", methods=["POST"])
def delete_stage(stage_id: int):
    stage = db.get_or_404(Stage, stage_id)
    roadmap_id = stage.roadmap_id
    db.session.delete(stage)
    db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap_id))


# --- Topic Routes ---
@app.route("/stage/<int:stage_id>/topic/create", methods=["POST"])
def create_topic(stage_id: int):
    stage = db.get_or_404(Stage, stage_id)
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    due_date = parse_date(request.form.get("due_date"))
    if title:
        topic = Topic(
            stage_id=stage.id,
            title=title,
            priority=priority,
            due_date=due_date,
            position=len(stage.topics),
        )
        db.session.add(topic)
        db.session.commit()
    return redirect(url_for("index", roadmap_id=stage.roadmap_id))


@app.route("/topic/<int:topic_id>/edit", methods=["POST"])
def edit_topic(topic_id: int):
    topic = db.get_or_404(Topic, topic_id)
    title = request.form.get("title", "").strip()
    if title:
        topic.title = title
        topic.status = request.form.get("status", topic.status)
        topic.priority = request.form.get("priority", topic.priority)
        topic.due_date = parse_date(request.form.get("due_date"))
        db.session.commit()
    return redirect(url_for("index", roadmap_id=topic.stage.roadmap_id))


@app.route("/topic/<int:topic_id>/cycle-status", methods=["POST"])
def cycle_topic_status(topic_id: int):
    topic = db.get_or_404(Topic, topic_id)
    cycle = {
        "not_started": "in_progress",
        "in_progress": "completed",
        "completed": "not_started",
    }
    topic.status = cycle.get(topic.status, "not_started")
    db.session.commit()
    return redirect(url_for("index", roadmap_id=topic.stage.roadmap_id))


@app.route("/topic/<int:topic_id>/delete", methods=["POST"])
def delete_topic(topic_id: int):
    topic = db.get_or_404(Topic, topic_id)
    roadmap_id = topic.stage.roadmap_id
    db.session.delete(topic)
    db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap_id))


# --- Project Routes ---
@app.route("/roadmap/<int:roadmap_id>/project/create", methods=["POST"])
def create_project(roadmap_id: int):
    roadmap = db.get_or_404(Roadmap, roadmap_id)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    stage_id = request.form.get("stage_id", type=int)
    status = request.form.get("status", "planned")
    tech_stack = request.form.get("tech_stack", "").strip()
    repo_url = request.form.get("repo_url", "").strip()
    due_date = parse_date(request.form.get("due_date"))

    if title:
        project = Project(
            roadmap_id=roadmap.id,
            stage_id=stage_id if stage_id else None,
            title=title,
            description=description,
            status=status,
            tech_stack=tech_stack,
            repo_url=repo_url,
            due_date=due_date,
        )
        db.session.add(project)
        db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap.id))


@app.route("/project/<int:project_id>/edit", methods=["POST"])
def edit_project(project_id: int):
    project = db.get_or_404(Project, project_id)
    title = request.form.get("title", "").strip()
    if title:
        stage_id = request.form.get("stage_id", type=int)
        project.title = title
        project.description = request.form.get("description", "").strip()
        project.stage_id = (
            stage_id
            if stage_id and db.session.get(Stage, stage_id)
            else None
        )
        project.status = request.form.get("status", project.status)
        project.tech_stack = request.form.get("tech_stack", "").strip()
        project.repo_url = request.form.get("repo_url", "").strip()
        project.due_date = parse_date(request.form.get("due_date"))
        db.session.commit()
    return redirect(url_for("index", roadmap_id=project.roadmap_id))


@app.route("/project/<int:project_id>/cycle-status", methods=["POST"])
def cycle_project_status(project_id: int):
    project = db.get_or_404(Project, project_id)
    cycle = {
        "planned": "in_progress",
        "in_progress": "completed",
        "completed": "planned",
    }
    project.status = cycle.get(project.status, "planned")
    db.session.commit()
    return redirect(url_for("index", roadmap_id=project.roadmap_id))


@app.route("/project/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id: int):
    project = db.get_or_404(Project, project_id)
    roadmap_id = project.roadmap_id
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap_id))


# --- Note Routes ---
@app.route("/roadmap/<int:roadmap_id>/note/create", methods=["POST"])
def create_note(roadmap_id: int):
    roadmap = db.get_or_404(Roadmap, roadmap_id)
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    stage_id = request.form.get("stage_id", type=int)
    topic_id = request.form.get("topic_id", type=int)

    if title and content:
        note = Note(
            roadmap_id=roadmap.id,
            stage_id=stage_id if stage_id else None,
            topic_id=topic_id if topic_id else None,
            title=title,
            content=content,
        )
        db.session.add(note)
        db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap.id))


@app.route("/note/<int:note_id>/edit", methods=["POST"])
def edit_note(note_id: int):
    note = db.get_or_404(Note, note_id)
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if title and content:
        stage_id = request.form.get("stage_id", type=int)
        topic_id = request.form.get("topic_id", type=int)
        note.title = title
        note.content = content
        note.stage_id = (
            stage_id if stage_id and db.session.get(Stage, stage_id) else None
        )
        note.topic_id = (
            topic_id if topic_id and db.session.get(Topic, topic_id) else None
        )
        db.session.commit()
    return redirect(url_for("index", roadmap_id=note.roadmap_id))


@app.route("/note/<int:note_id>/delete", methods=["POST"])
def delete_note(note_id: int):
    note = db.get_or_404(Note, note_id)
    roadmap_id = note.roadmap_id
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("index", roadmap_id=roadmap_id))


# --- Calendar Routes ---
@app.route("/calendar")
def calendar_view():
    return render_template("calendar.html")


@app.route("/api/calendar/events")
def calendar_events_api():
    topics = Topic.query.filter(Topic.due_date.isnot(None)).all()
    projects = Project.query.filter(Project.due_date.isnot(None)).all()

    events = []
    for t in topics:
        events.append(
            {
                "id": f"topic-{t.id}",
                "type": "Topic",
                "title": t.title,
                "date": t.due_date.isoformat(),
                "status": t.status,
                "priority": t.priority,
                "roadmap": t.stage.roadmap.title,
                "roadmap_id": t.stage.roadmap_id,
                "color": t.stage.roadmap.color_hex,
            }
        )
    for p in projects:
        events.append(
            {
                "id": f"project-{p.id}",
                "type": "Project",
                "title": p.title,
                "date": p.due_date.isoformat(),
                "status": p.status,
                "priority": "high",
                "roadmap": p.roadmap.title,
                "roadmap_id": p.roadmap_id,
                "color": p.roadmap.color_hex,
            }
        )
    return jsonify(events)

import json
from flask import Response, flash

# --- JSON Backup & Import Routes ---
@app.route("/api/export/json")
def export_json():
  roadmaps = Roadmap.query.all()
  data = []
  
  for rm in roadmaps:
    rm_dict = {
      "title": rm.title,
      "description": rm.description,
      "color_hex": rm.color_hex,
      "stages": [],
      "projects": [],
      "notes": []
    }
    
    for s in rm.stages:
      s_dict = {
        "title": s.title,
        "description": s.description,
        "position": s.position,
        "topics": [{
          "title": t.title,
          "status": t.status,
          "priority": t.priority,
          "due_date": t.due_date.isoformat() if t.due_date else None,
          "position": t.position
        } for t in s.topics]
      }
      rm_dict["stages"].append(s_dict)
      
    for p in rm.projects:
      rm_dict["projects"].append({
        "title": p.title,
        "description": p.description,
        "status": p.status,
        "tech_stack": p.tech_stack,
        "repo_url": p.repo_url,
        "due_date": p.due_date.isoformat() if p.due_date else None
      })
      
    for n in rm.notes:
      rm_dict["notes"].append({
        "title": n.title,
        "content": n.content
      })
      
    data.append(rm_dict)

  json_data = json.dumps(data, indent=2)
  return Response(
    json_data,
    mimetype="application/json",
    headers={"Content-Disposition": "attachment;filename=roadmap_backup.json"}
  )

@app.route("/roadmap/import", methods=["POST"])
def import_json():
  file = request.files.get("file")
  if not file:
    return redirect(url_for("index"))
    
  try:
    content = file.read().decode("utf-8")
    data = json.loads(content)
    
    if not isinstance(data, list):
      data = [data]
      
    for rm_data in data:
      roadmap = Roadmap(
        title=rm_data.get("title", "Imported Roadmap"),
        description=rm_data.get("description"),
        color_hex=rm_data.get("color_hex", "#3b82f6")
      )
      db.session.add(roadmap)
      db.session.flush() # Get roadmap.id
      
      # Map stage titles to new stage objects for notes/projects reference if needed
      stage_map = {}
      for s_data in rm_data.get("stages", []):
        stage = Stage(
          roadmap_id=roadmap.id,
          title=s_data.get("title", "Stage"),
          description=s_data.get("description"),
          position=s_data.get("position", 0)
        )
        db.session.add(stage)
        db.session.flush()
        stage_map[stage.title] = stage.id
        
        for t_data in s_data.get("topics", []):
          topic = Topic(
            stage_id=stage.id,
            title=t_data.get("title", "Topic"),
            status=t_data.get("status", "not_started"),
            priority=t_data.get("priority", "medium"),
            due_date=parse_date(t_data.get("due_date")),
            position=t_data.get("position", 0)
          )
          db.session.add(topic)
          
      for p_data in rm_data.get("projects", []):
        project = Project(
          roadmap_id=roadmap.id,
          title=p_data.get("title", "Project"),
          description=p_data.get("description"),
          status=p_data.get("status", "planned"),
          tech_stack=p_data.get("tech_stack"),
          repo_url=p_data.get("repo_url"),
          due_date=parse_date(p_data.get("due_date"))
        )
        db.session.add(project)
        
      for n_data in rm_data.get("notes", []):
        note = Note(
          roadmap_id=roadmap.id,
          title=n_data.get("title", "Note"),
          content=n_data.get("content", "")
        )
        db.session.add(note)
        
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(f"Import error: {e}")
    
  return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
