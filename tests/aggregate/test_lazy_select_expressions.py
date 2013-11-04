from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy_utils.aggregates import aggregated_attr
from tests import TestCase


class TestLazyEvaluatedSelectExpressionsForAggregates(TestCase):
    dns = 'postgres://postgres@localhost/sqlalchemy_utils_test'

    def create_models(self):
        class Catalog(self.Base):
            __tablename__ = 'catalog'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))

            @aggregated_attr('products')
            def net_worth(self):
                return sa.Column(sa.Numeric, default=0)

            @net_worth.expression
            def net_worth_expr(self):
                return sa.func.sum(Product.price)

            products = sa.orm.relationship('Product', backref='catalog')

        class Product(self.Base):
            __tablename__ = 'product'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            price = sa.Column(sa.Numeric)

            catalog_id = sa.Column(sa.Integer, sa.ForeignKey('catalog.id'))

        self.Catalog = Catalog
        self.Product = Product

    def test_assigns_aggregates(self):
        catalog = self.Catalog(
            name=u'Some catalog'
        )
        self.session.add(catalog)
        self.session.commit()
        product = self.Product(
            name=u'Some product',
            price=Decimal('1000'),
            catalog=catalog
        )
        self.session.add(product)
        self.session.commit()
        self.session.refresh(catalog)
        assert catalog.net_worth == Decimal('1000')
