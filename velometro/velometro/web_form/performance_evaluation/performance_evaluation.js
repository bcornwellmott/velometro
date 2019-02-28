frappe.ready(function() {
	// bind events here
	
	frappe.is_new = 0
	frappe.login_required = 0
	
	{% if active_reviews %}
		$('.review_table').html(`
		<h3>Previous Reviews</h3>
			<table> 
				<tr>
					<th>
						Review Name
					</th>
					<th>
						Employee
					</th>
					<th>
						Rating
					</th>
					<th>
						Comment
					</th>
				</tr>
				{% for review in active_reviews %}
					<tr>
						<td>
							<a href='/performance-evaluation?name={{ review[0] }}'>{{ review[0] }}</a>
						</td>
						<td>
							{{ review[1] }}
						</td>
						<td>
							{% if review[2] == 'Unicorn' %}
								<img src="unicorn.jpg" width="50">
							{% elif review[2] == 'Shruggy' %}
								<img src="shruggy.jpg" width="50">
							{% elif review[2] == 'Banana Peel' %}
								<img src="banana.jpg" width="50">
							{% endif %}
						</td>
						<td>
							{{ review[3] }}
						</td>
					</tr>
				
				{% endfor %}
			</table> 
		`);
	{% endif %}
	
	{% if employee_names %}
		var selectBox = "<h3>Employee</h3><select class='employeeSelect' onChange='updateEmployee(this)'>";
		{% for name in employee_names %}
			selectBox += "<option  value='{{ name[0] }}'>{{ name[1] }}</option>"
		{% endfor %}
		selectBox += "</select>";
		$('.employee_header').html(selectBox);
	{% endif %}
	
	
	
	$('.rating_header').html(`
		<h3>Rating</h3>
		<table> 
			<tr>
				<td valign="bottom">
					<img src="unicorn.jpg" width="200">
					<br>
					<input type="radio" name="rating" value="Unicorn" class="ratingsRadio" onclick="updateRating(this)">
				</td>
				<td valign="bottom">
					<img src="shruggy.jpg" width="200">
					<br>
					<input type="radio" name="rating" value="Shruggy" class="ratingsRadio" onclick="updateRating(this)">
				</td>
				<td valign="bottom">
					<img src="banana.jpg" width="200">
					<br>
					<input type="radio" name="rating" value="Banana Peel" class="ratingsRadio" onclick="updateRating(this)">
				</td>
			</tr>
		</table> <div id="unicornAnimation"><img src="unicorn.png" width="100%"></div>
	`);
	

				
	/*$(".btn-form-submit").on("click", function () {
		window.location.href = window.location.pathname + "?new=1"
		return false;
	});*/

	var $form = $("form[data-web-form='" + frappe.web_form_name + "']");
	$form.find("[name][data-doctype='" + frappe.web_form_doctype + "']").each(function () {
		var $input = $(this);
		if ($input.attr("data-label") === "Rating") {
			$input["0"].parentElement.hidden = true;
			$('.ratingsRadio').val([$input["0"].value]);
			
		}
		if ($input.attr("data-label") === "target_employee") {
			$input["0"].parentElement.hidden = true;
			$('.employeeSelect').val($input["0"].value);
		}
	})
	
})

function updateEmployee(sel)
{

	var $form = $("form[data-web-form='" + frappe.web_form_name + "']");
	$form.find("[name][data-doctype='" + frappe.web_form_doctype + "']").each(function () {
		var $input = $(this);
		if ($input.attr("data-label") === "target_employee") {
			var val = sel[sel.selectedIndex].value;
			$input[0].value = val;
		}
	})
			
}
function updateRating(sel)
{

	var $form = $("form[data-web-form='" + frappe.web_form_name + "']");
	$form.find("[name][data-doctype='" + frappe.web_form_doctype + "']").each(function () {
		var $input = $(this);
		if ($input.attr("data-label") === "Rating") {
			$input[0].value = sel.value;
			if(sel.value === "Unicorn")
			{
				myMove();
			}
		}
	})
			
}

function myMove() {
    var elem = document.getElementById("unicornAnimation"); 
	
    var posx = 1100;
    var posy = -400;
    var id = setInterval(frame, 10);
    function frame() {
        if (posx < - 400) {
			elem.style.display = "none";
            clearInterval(id);
        } else {
            posy+=4; 
            posx-=6; 
            elem.style.top = posx + 'px'; 
            elem.style.left = posy + 'px'; 
			elem.style.display = "block";
        }
    }
}