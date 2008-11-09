jQuery.fn.swap = function(b) {
	b = jQuery(b)[0];
	var a = this[0];

	var t = a.parentNode.insertBefore(document.createTextNode(''), a);
	b.parentNode.insertBefore(a, b);
	t.parentNode.insertBefore(b, t);
	t.parentNode.removeChild(t);

	return this;
};

$(function() {
	$('.delete-link').click(function() {
		var item = $(this).parents('li');
		var item_id = item.attr('id').split('-', 2)[1];

		$('.ajax', item).show();

		$.ajax({
			url: '/a/item/delete/' + item_id,
			success: function() {
				item.slideUp(500);
			},
			error: function(request, textStatus, errorThrown) {
				alert('Error');
				$('.ajax', item).hide();
			}
		});

		return false;
	});

	$('.up-link').click(function() {
		return move('up', this);
	});

	$('.down-link').click(function() {
		return move('down', this);
	});
		
	function move (direction, link) {
		var item = $(link).parents('li');
		var item_id = item.attr('id').split('-', 2)[1];

		$('.ajax', item).show();

		$.ajax({
			url: '/a/item/' + direction + '/' + item_id,
			success: function(data) {
				if (data) {
					var other_item = $('#item-' + data);
					$(other_item).fadeOut(300, function() {
						$(item).swap($(other_item));
						$(item).fadeIn();
						$(other_item).fadeIn();
					});
				} else {
					location.reload();
				}
			},
			error: function(request, textStatus, errorThrown) {
				alert('Error');
				$('.ajax', item).hide();
			}
		});

		return false;
	}

	function refresh_queue() {
		$('#refresh-ajax').show();

		$.ajax({
			url: '/a/xhr_queue',
			success: function(html) {
				$('#queue').html(html);
			},
			complete: function() {
				$('#refresh-ajax').hide();
			}
		});

		return false;
	}

	$('.refresh-link').click(function() {
		return refresh_queue();
	});

	function auto_refresh() {
		refresh_queue();
		setTimeout(auto_refresh, 3000);
	}

	if ($('#queue')) {
		setTimeout(auto_refresh, 3000);
	}
});
