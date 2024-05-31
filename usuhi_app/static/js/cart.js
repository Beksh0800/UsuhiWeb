document.addEventListener("DOMContentLoaded", function () {
    console.log('Cart script loaded');

    function saveCartToLocalStorage() {
        let cartItems = [];
        document.querySelectorAll('.cart-item').forEach(item => {
            let nameElement = item.querySelector('.card-title').textContent.trim();
            let priceElement = item.querySelector('.card-body h4').textContent.trim();
            let quantityElement = item.querySelector('.quantity').textContent.trim();
            cartItems.push({name: nameElement, price: priceElement, quantity: quantityElement});
        });
        localStorage.setItem('cart_items', JSON.stringify(cartItems));
        let totalPrice = document.getElementById('total-price').textContent.trim();
        localStorage.setItem('total_price', totalPrice);
    }

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
                cartQuantityElement.innerHTML = `${quantity}`;
                cartQuantityElement.classList.add('btn-success');
                cartQuantityElement.classList.remove('btn-primary');
            } else {
                cartQuantityElement.innerHTML = `<i class="bi bi-cart"></i>`;
                cartQuantityElement.classList.add('btn-primary');
                cartQuantityElement.classList.remove('btn-success');
            }
        }
    }

    function updateTotalDisplay(total) {
        const totalElement = document.getElementById('total-price');
        if (totalElement) {
            totalElement.innerHTML = `${total}₸`;
            saveCartToLocalStorage();
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

    function updateTotalPrice() {
        $.ajax({
            type: 'GET',
            url: '/cart/total/',
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    updateTotalDisplay(response.total_price);
                } else {
                    alert('Ошибка при обновлении общей суммы: ' + response.error);
                }
            },
            error: function (xhr, textStatus, error) {
                alert('Произошла ошибка при обновлении общей суммы: ' + error);
            }
        });
    }

    function handleButtonClick(button, action) {
        const foodId = parseInt(button.dataset.foodId);
        if (isNaN(foodId)) {
            alert('Ошибка: food_id должен быть числом!');
            return;
        }

        const csrfToken = getCookie('csrftoken');
        disableButtons([button]);

        let url, data;
        if (action === 'add') {
            url = button.dataset.addToCartUrl;
            data = {
                'food_id': foodId,
                'quantity': 1,
                'action': 'add'
            };
        } else if (action === 'remove') {
            url = '/remove_from_cart/';
            data = {
                'food_id': foodId
            };
        } else if (action === 'increase') {
            url = '/modify_cart/';
            data = {
                'food_id': foodId,
                'quantity': 1,
                'action': 'add'
            };
        } else if (action === 'reduce') {
            url = '/modify_cart/';
            data = {
                'food_id': foodId,
                'quantity': 1,
                'action': 'remove'
            };
        }

        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            headers: {
                'X-CSRFToken': csrfToken
            },
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    if (action === 'remove' || action === 'reduce') {
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
                        updateCartDisplay(foodId, response.quantity);
                    }
                    updateTotalPrice();  // Обновление общей суммы
                } else {
                    alert('Ошибка при выполнении действия: ' + response.error);
                }
            },
            error: function (xhr, textStatus, error) {
                alert('Произошла ошибка при выполнении запроса: ' + error);
            },
            complete: function () {
                enableButtons([button]);
            }
        });
    }

    addToCartButtons.forEach(button => {
        const foodId = parseInt(button.dataset.foodId);
        const initialQuantity = parseInt(button.getAttribute('data-quantity')) || 0;
        updateCartDisplay(foodId, initialQuantity);

        button.addEventListener('click', function () {
            handleButtonClick(button, 'add');
        });
    });

    removeFromCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            handleButtonClick(button, 'remove');
            updateCartDisplay();
        });
    });

    increaseQuantityButtons.forEach(button => {
        button.addEventListener('click', function () {
            handleButtonClick(button, 'increase');
        });
    });

    reduceQuantityButtons.forEach(button => {
        button.addEventListener('click', function () {
            handleButtonClick(button, 'reduce');
        });
    });

    // Инициализация состояния при загрузке страницы
    checkIfCartIsEmpty();
    updateTotalPrice();
    updateCartDisplay();
});
