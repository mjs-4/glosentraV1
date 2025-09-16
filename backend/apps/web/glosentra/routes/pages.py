"""Page routes for Glosentra web interface."""

from flask import Blueprint, render_template, current_app

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    """Home page with hero and feature cards."""
    return render_template('index.html')


@pages_bp.route('/deploy')
def deploy():
    """Deploy page redirect."""
    return render_template('deploy_detect.html')


@pages_bp.route('/deploy/detect')
def deploy_detect():
    """Object detection deployment page."""
    return render_template('deploy_detect.html')


@pages_bp.route('/deploy/segment')
def deploy_segment():
    """Instance segmentation deployment page."""
    return render_template('deploy_segment.html')


@pages_bp.route('/deploy/classify')
def deploy_classify():
    """Image classification deployment page."""
    return render_template('deploy_classify.html')


@pages_bp.route('/deploy/pose')
def deploy_pose():
    """Pose estimation deployment page."""
    return render_template('deploy_pose.html')


@pages_bp.route('/realtime')
def realtime():
    """Real-time inference page."""
    return render_template('realtime.html')


@pages_bp.route('/analytics')
def analytics():
    """Analytics dashboard page."""
    return render_template('analytics.html')


@pages_bp.route('/docs')
def docs():
    """Documentation search page."""
    return render_template('docs.html')


@pages_bp.route('/finetune')
def finetune():
    """Fine-tuning guide page."""
    return render_template('finetune.html')

@pages_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')
