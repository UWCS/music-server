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
});
