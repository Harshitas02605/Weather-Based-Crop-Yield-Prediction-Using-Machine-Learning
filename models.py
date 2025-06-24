from datetime import datetime, timezone, timedelta;
from sqlalchemy.orm import Mapped, mapped_column, relationship; # type: ignore
from CropMaster import db, login_manager;
from flask_login import UserMixin;

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

def get_ist_time():
    IST = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(IST)

class User(db.Model, UserMixin):
    __tablename__ = 'user';

    id: Mapped[int] = mapped_column(primary_key=True);

    user_category: Mapped[str] = mapped_column(nullable=False, default='Farmer');

    username: Mapped[str] = mapped_column(db.String(20), nullable=False);

    email: Mapped[str] = mapped_column(db.String(40), nullable=False);

    password: Mapped[str] = mapped_column(db.String(40), nullable=False);

    results: Mapped[list['ResultOfUsers']] = relationship(back_populates='user');

class ResultOfUsers(db.Model):
    __tablename__ = 'resultOfUsers';

    id: Mapped[int] = mapped_column(primary_key=True);

    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False);

    state: Mapped[str] = mapped_column(db.String(75), nullable=False);

    district: Mapped[str] = mapped_column(db.String(100), nullable=False);

    season: Mapped[str] = mapped_column(db.String(50), nullable=False);

    average_temp: Mapped[float] = mapped_column(db.Float, nullable=False);

    average_rainfall: Mapped[float] = mapped_column(db.Float, nullable=False);

    crop: Mapped[str] = mapped_column(db.String(100), nullable=False)

    predicted_amount: Mapped[float] = mapped_column(db.Float, nullable=False);

    prompted_at: Mapped[datetime] = mapped_column(default=get_ist_time, nullable=False);

    user: Mapped['User'] = relationship(back_populates='results');
