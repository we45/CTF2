

EXAMPLE.MODELS.UserModel = Backbone.Model.extend({
  
	initialize: function() {
	},
	
	urlRoot : function(){
    	return '/api/CTF/appointments/';
	},
	
});


var Users = Backbone.Collection.extend({

	model: EXAMPLE.MODELS.UserModel,
	
	url : '/api/CTF/appointments/',
	
});

EXAMPLE.COLLECTIONS.Users = new Users;