function popUp(url){
	self.name = "main_window";
	
	popup_window = window.open(
	 url, "popup_window",
	 'toolbar=no,location=0,directories=0,status=0,menubar=0,scrollbars=yes,resizable=yes,width=530,height=400'
	);
	popup_window.focus();
}
