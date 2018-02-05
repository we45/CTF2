app.models.UserModel = Backbone.Model.extend({
  
	initialize: function() {
	},
	
	urlRoot : function(){
    	return '/api/CTF/user/';
	},
	
});


var Users = Backbone.Collection.extend({

	model: app.models.UserModel,
	
	url : '/api/CTF/user/',
	
});

app.collections.Users = new Users;

app.views.appListItem = Backbone.View.extend({ 
	
	tagName : 'div',

	initialize : function(model, options){
		this.options = options
	},

	events : {
	},

	template : _.template("<div>username: <%- username %> email: <%- email %> </div>"),
	

	render : function() {
		this.$el.html(this.template(this.model.toJSON()));
		return this;
	}
});


app.views.appList = Backbone.View.extend({ 
	
	el : "#my-model-list",
  
	
	initialize : function(options){
		this.listenTo(app.collections.Users, 'reset', this.addAll, this);
	},
	
	addOne : function(model) {
		var view = new app.views.appListItem ({ model : model })
		console.log( view.render().el )
		this.$el.append(view.render().el)
	},
	
	addAll : function(){    
		var that = this;
		app.collections.Users.each(function(model){
			that.addOne(model);
		});
	},
  
	render : function() {
		this.$el.html(this.template());
		return this;
	}
	
});