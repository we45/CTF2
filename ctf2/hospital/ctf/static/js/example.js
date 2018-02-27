EXAMPLE.VIEWS.ExampleListItem = Backbone.View.extend({ 
	
	tagName : 'tr',

	initialize : function(model, options){
		this.options = options
	},

	events : {
	},

	template : _.template("<td><%= patient.name %></td>"+
                        "<td><%- patient.email %></td>"+
                        "<td><%- patient.gender %></td>"+
                        "<td><%- patient.gender %></td>"),
                    //     "<a href='#' data-href='/patient/delete/<%- id %>/' data-toggle='modal' data-target='#confirm-delete' class='btn btn-xs btn-danger pull-right delete-confirmation' title='Delete'>"+
                    // "<span class='fa fa-trash-o'></span>"+
                    // "</a>"),
	

	render : function() {
		this.$el.html(this.template(this.model.toJSON()));
		return this;
	}
});


EXAMPLE.VIEWS.ExampleList = Backbone.View.extend({ 
	
	el : "#my-model-list",
  
	
	initialize : function(options){
		this.listenTo(EXAMPLE.COLLECTIONS.Users, 'reset', this.addAll, this);
	},
	
	addOne : function(model) {
		var view = new EXAMPLE.VIEWS.ExampleListItem ({ model : model })
		// console.log( view.render().el )
		this.$el.append(view.render().el)
	},
	
	addAll : function(){    
		var that = this;
		EXAMPLE.COLLECTIONS.Users.each(function(model){
			that.addOne(model);
		});
	},
  
	render : function() {
		this.$el.html(this.template());
		return this;
	}
	
});