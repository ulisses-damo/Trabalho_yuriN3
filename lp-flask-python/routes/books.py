import datetime
from flask import request, jsonify
from sqlalchemy import asc, desc

from app import app, db
from jwt import generate_jwt
from model.books import Book
from model.books import Review



@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()

    if not all(key in data for key in ['title', 'author']):
        return jsonify({'message': 'Campos obrigatórios: title e author'}), 400

    new_book = Book(
        title=data['title'],
        author=data['author'],
        description=data.get('description', '')
    )
    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        'id': new_book.id,
        'title': new_book.title,
        'author': new_book.author,
        'description': new_book.description
    }), 201


@app.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()

    result = []
    for book in books:
        reviews = Review.query.filter_by(book_id=book.id).all()
        classificação_media = (
            sum([review.rating for review in reviews]) / len(reviews)
            if reviews else None
        )
        result.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'classificação_media': classificação_media,
            'total_reviews': len(reviews)
        })

    return jsonify(result), 200


@app.route('/books/<int:book_id>/reviews', methods=['POST'])
def add_review(book_id):
    data = request.get_json()

    if not all(key in data for key in ['user_id', 'rating']):
        return jsonify({'message': 'Campos obrigatórios: user_id e rating'}), 400

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': 'Livro não encontrado'}), 404

    new_review = Review(
        user_id=data['user_id'],
        book_id=book_id,
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    db.session.add(new_review)
    db.session.commit()

    return jsonify({
        'id': new_review.id,
        'user_id': new_review.user_id,
        'book_id': new_review.book_id,
        'rating': new_review.rating,
        'comment': new_review.comment
    }), 201


@app.route('/books/<int:book_id>/reviews', methods=['GET'])
def list_reviews(book_id):
    reviews = Review.query.filter_by(book_id=book_id).all()
    if not reviews:
        return jsonify({'message': 'Nenhuma avaliação encontrada para este livro'}), 404

    result = [{
        'id': review.id,
        'user_id': review.user_id,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at
    } for review in reviews]

    return jsonify(result), 200
