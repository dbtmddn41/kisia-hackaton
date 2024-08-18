from flask import Blueprint, render_template, session, g, redirect, url_for

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def main():
    return "hello world"