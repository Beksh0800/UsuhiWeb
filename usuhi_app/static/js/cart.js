document.addEventListener("DOMContentLoaded", function () {
    const reduceQuantityButtons = document.querySelectorAll('.reduce-quantity-btn');
    const increaseQuantityButtons = document.querySelectorAll('.increase-quantity-btn');
    const removeFromCartButtons = document.querySelectorAll('.remove-from-cart-btn');
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');

    function disableButtons(buttons) {
        buttons.forEach(button => button.disabled = true);
    }

    function enableButtons(buttons) {
        buttons.forEach(button => button.disabled = false);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateCartDisplay(foodId, quantity) {
        const cartQuantityElement = document.getElementById(`cart-quantity-${foodId}`);

        if (cartQuantityElement) {
            if (quantity > 0) {
                cartQuantityElement.textContent = `В корзине (${quantity})`;
                cartQuantityElement.classList.add('btn-success');
                cartQuantityElement.classList.remove('btn-primary');
            } else if (quantity === 0) {
                cartQuantityElement.textContent = "Добавить в корзину";
                cartQuantityElement.classList.add('btn-primary');
                cartQuantityElement.classList.remove('btn-success');
            }
        }
    }

    function checkIfCartIsEmpty() {
        const cartItems = document.querySelectorAll('.cart-item');
        const cartEmptyMessage = document.getElementById('cart-empty-message');

        if (cartEmptyMessage) {
            if (cartItems.length === 0) {
                cartEmptyMessage.style.display = 'block';
            } else {
                cartEmptyMessage.style.display = 'none';
            }
        }
    }

    // Инициализация состояния при загрузке страницы
    checkIfCartIsEmpty();

    addToCartButtons.forEach(button => {
        const foodId = parseInt(button.dataset.foodId);
        const initialQuantity = parseInt(button.getAttribute('data-quantity')) || 0;
        updateCartDisplay(foodId, initialQuantity);

        button.addEventListener('click', function () {
            const foodId = parseInt(button.dataset.foodId);

            if (isNaN(foodId)) {
                alert('Ошибка: food_id должен быть числом!');
                return;
            }

            const csrfToken = getCookie('csrftoken');
            disableButtons([button]);

            $.ajax({
                type: 'POST',
                url: button.dataset.addToCartUrl,
                data: {
                    'food_id': foodId,
                    'quantity': 1,
                    'action': 'add'
                },
                headers: {
                    'X-CSRFToken': csrfToken
                },
                dataType: 'json',
                success: function (response) {
                    if (response.success) {
                        updateCartDisplay(foodId, response.quantity);
                    } else {
                        alert('Ошибка при добавлении товара в корзину: ' + response.error);
                    }
                },
                error: function (xhr, textStatus, error) {
                    alert('Произошла ошибка при выполнении запроса: ' + error);
                },
                complete: function () {
                    enableButtons([button]);
                }
            });
        });
    });

    removeFromCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            const foodId = parseInt(button.dataset.foodId);

            if (isNaN(foodId)) {
                alert('Ошибка: food_id должен быть числом!');
                return;
            }

            const csrfToken = getCookie('csrftoken');
            disableButtons([button]);

            $.ajax({
                type: 'POST',
                url: '/remove_from_cart/',
                data: {
                    'food_id': foodId
                },
                headers: {
                    'X-CSRFToken': csrfToken
                },
                dataType: 'json',
                success: function (response) {
                    if (response.success) {
                        updateCartDisplay(foodId, 0);
                        const cartItemElement = document.getElementById(`cart-item-${foodId}`);
                        if (cartItemElement) {
                            cartItemElement.remove();
                        }
                        checkIfCartIsEmpty();
                    } else {
                        alert('Ошибка при удалении товара из корзины: ' + response.error);
                    }
                },
                error: function (xhr, textStatus, error) {
                    alert('Произошла ошибка при выполнении запроса: ' + error);
                },
                complete: function () {
                    enableButtons([button]);
                }
            });
        });
    });

    increaseQuantityButtons.forEach(button => {
        button.addEventListener('click', function () {
            const foodId = parseInt(button.dataset.foodId);
            const csrfToken = getCookie('csrftoken');
            disableButtons([button]);

            $.ajax({
                type: 'POST',
                url: '/modify_cart/',
                data: {
                    'food_id': foodId,
                    'quantity': 1,
                    'action': 'add'
                },
                headers: {
                    'X-CSRFToken': csrfToken
                },
                dataType: 'json',
                success: function (response) {
                    if (response.success) {
                        updateCartDisplay(foodId, response.quantity);
                    } else {
                        alert('Ошибка при изменении количества товара в корзине: ' + response.error);
                    }
                },
                error: function (xhr, textStatus, error) {
                    alert('Произошла ошибка при выполнении запроса: ' + error);
                },
                complete: function () {
                    enableButtons([button]);
                }
            });
        });
    });

    reduceQuantityButtons.forEach(button => {
        button.addEventListener('click', function () {
            const foodId = parseInt(button.dataset.foodId);
            const csrfToken = getCookie('csrftoken');
            disableButtons([button]);

            $.ajax({
                type: 'POST',
                url: '/modify_cart/',
                data: {
                    'food_id': foodId,
                    'quantity': 1,
                    'action': 'remove'
                },
                headers: {
                    'X-CSRFToken': csrfToken
                },
                dataType: 'json',
                success: function (response) {
                    if (response.success) {
                        if (response.quantity > 0) {
                            updateCartDisplay(foodId, response.quantity);
                        } else {
                            const cartItemElement = document.getElementById(`cart-item-${foodId}`);
                            if (cartItemElement) {
                                cartItemElement.remove();
                            }
                            updateCartDisplay(foodId, response.quantity);
                            checkIfCartIsEmpty();
                        }
                    } else {
                        alert('Ошибка при изменении количества товара в корзине: ' + response.error);
                    }
                },
                error: function (xhr, textStatus, error) {
                    alert('Произошла ошибка при выполнении запроса: ' + error);
                },
                complete: function () {
                    enableButtons([button]);
                }
            });
        });
    });

    // Инициализация состояния кнопок при загрузке страницы
    addToCartButtons.forEach(button => {
        const foodId = parseInt(button.dataset.foodId);
        const initialQuantity = parseInt(button.getAttribute('data-quantity')) || 0;
        updateCartDisplay(foodId, initialQuantity);
    });
});
