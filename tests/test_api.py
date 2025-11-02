import uuid
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

BASE_URL = "http://localhost:8000"


class TestWalletAPI:
    """Тесты для API кошельков через HTTP запросы."""

    @pytest.fixture
    def wallet_id(self):
        """Генерирует уникальный ID для кошелька."""
        return str(uuid.uuid4())

    def test_create_and_get_wallet(self, wallet_id):
        """Тест создания кошелька и получения баланса."""
        with httpx.Client() as client:
            # Создаем кошелек
            response = client.post(
                f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == wallet_id
            assert data["balance"] == "0.00"

            # Получаем баланс
            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["balance"] == "0.00"

    def test_deposit_operation(self, wallet_id):
        """Тест операции пополнения."""
        with httpx.Client() as client:
            # Создаем кошелек
            response = client.post(
                f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id}
            )
            assert response.status_code == 200

            # Пополняем счет
            response = client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": 1500},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["operation_type"] == "DEPOSIT"
            # Amount в транзакции может быть без .00 для целых чисел
            assert data["amount"] in ["1500", "1500.00"]

            # Проверяем баланс (баланс всегда с двумя знаками)
            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            assert response.status_code == 200
            assert response.json()["balance"] == "1500.00"

    def test_withdraw_operation(self, wallet_id):
        """Тест операции снятия."""
        with httpx.Client() as client:
            # Создаем кошелек и пополняем
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})
            client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": 1000},
            )

            # Снимаем средства
            response = client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": 300},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["operation_type"] == "WITHDRAW"
            assert data["amount"] in ["300", "300.00"]

            # Проверяем баланс
            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            assert response.status_code == 200
            assert response.json()["balance"] == "700.00"

    def test_insufficient_funds(self, wallet_id):
        """Тест недостаточных средств."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            # Пытаемся снять больше, чем есть
            response = client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": 500},
            )
            assert response.status_code == 400
            assert "insufficient funds" in response.json()["detail"].lower()

    def test_wallet_not_found(self):
        """Тест запроса несуществующего кошелька."""
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/api/v1/wallets/non-existent-wallet")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_duplicate_wallet(self, wallet_id):
        """Тест создания дубликата кошелька."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            response = client.post(
                f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id}
            )
            assert response.status_code == 400
            assert "already exists" in response.json()["detail"].lower()


class TestWalletOperationsAdvanced:
    """Продвинутые тесты операций."""

    @pytest.fixture
    def wallet_id(self):
        return str(uuid.uuid4())

    def test_multiple_operations(self, wallet_id):
        """Тест последовательности операций."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            # Последовательность операций
            operations = [
                ("DEPOSIT", 1000),
                ("WITHDRAW", 200),
                ("DEPOSIT", 500),
                ("WITHDRAW", 300),
            ]

            for op_type, amount in operations:
                response = client.post(
                    f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                    json={"operation_type": op_type, "amount": amount},
                )
                assert response.status_code == 200

            # Проверяем итоговый баланс: 1000 - 200 + 500 - 300 = 1000
            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            assert response.json()["balance"] == "1000.00"

    def test_decimal_precision(self, wallet_id):
        """Тест точности десятичных операций."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            # Операции с дробными суммами
            operations = [
                ("DEPOSIT", 0.01),
                ("DEPOSIT", 0.02),
                ("DEPOSIT", 0.03),
            ]

            for op_type, amount in operations:
                response = client.post(
                    f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                    json={"operation_type": op_type, "amount": amount},
                )
                assert response.status_code == 200

            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            assert response.json()["balance"] == "0.06"

    def test_large_amounts(self, wallet_id):
        """Тест операций с большими суммами."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            large_amount = 999999.99
            response = client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": large_amount},
            )
            assert response.status_code == 200

            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            assert response.json()["balance"] == "999999.99"


class TestConcurrency:
    """Тесты конкурентности."""

    @pytest.fixture
    def wallet_id(self):
        return str(uuid.uuid4())

    def test_concurrent_deposits(self, wallet_id):
        """Тест параллельных пополнений."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

        num_operations = 5
        amount_per_operation = 100

        def make_deposit():
            with httpx.Client() as client:
                response = client.post(
                    f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                    json={"operation_type": "DEPOSIT", "amount": amount_per_operation},
                )
                return response.status_code

        # Запускаем операции параллельно
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_deposit) for _ in range(num_operations)]
            results = [future.result() for future in futures]

        # Все операции должны завершиться успешно
        assert all(result == 200 for result in results)

        # Проверяем итоговый баланс - баланс всегда с двумя знаками
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            expected_balance = num_operations * amount_per_operation
            assert response.json()["balance"] == f"{expected_balance}.00"

    def test_concurrent_mixed_operations(self, wallet_id):
        """Тест параллельных операций пополнения и снятия."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            # Начальный депозит
            client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": 1000},
            )

        def make_operation(op_type, amount):
            with httpx.Client() as client:
                response = client.post(
                    f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                    json={"operation_type": op_type, "amount": amount},
                )
                return response.status_code

        # Запускаем смешанные операции параллельно
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(3):  # 3 депозита и 3 снятия
                futures.append(executor.submit(make_operation, "DEPOSIT", 100))
                futures.append(executor.submit(make_operation, "WITHDRAW", 50))

            results = [future.result() for future in futures]

        # Все операции должны завершиться успешно
        assert all(result == 200 for result in results)

        # Проверяем итоговый баланс: 1000 + (3*100) - (3*50) = 1000 + 300 - 150 = 1150
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/api/v1/wallets/{wallet_id}")
            assert response.json()["balance"] == "1150.00"


class TestErrorCases:
    """Тесты обработки ошибок."""

    @pytest.fixture
    def wallet_id(self):
        return str(uuid.uuid4())

    def test_invalid_operation_type(self, wallet_id):
        """Тест невалидного типа операции."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            response = client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "INVALID_TYPE", "amount": 100},
            )
            # FastAPI возвращает 422 при ошибках валидации
            assert response.status_code == 422

    def test_negative_amount(self, wallet_id):
        """Тест отрицательной суммы."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            response = client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": -100},
            )
            assert response.status_code == 422

    def test_zero_amount(self, wallet_id):
        """Тест нулевой суммы."""
        with httpx.Client() as client:
            client.post(f"{BASE_URL}/api/v1/wallets/", json={"id": wallet_id})

            response = client.post(
                f"{BASE_URL}/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": 0},
            )
            assert response.status_code == 422

    def test_operation_nonexistent_wallet(self):
        """Тест операции на несуществующем кошельке."""
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/api/v1/wallets/non-existent/operation",
                json={"operation_type": "DEPOSIT", "amount": 100},
            )
            assert response.status_code == 400
            assert "not found" in response.json()["detail"].lower()


def test_health_check():
    """Тест проверки здоровья приложения."""
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_api_documentation():
    """Тест доступности документации API."""
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
