from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from .models import BlogPost, BlogComment
from .forms import CommentForm

class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).select_related('author')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
            
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__icontains=query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all unique categories for the sidebar
        context['categories'] = BlogPost.objects.filter(
            status='published'
        ).values_list('category', flat=True).distinct()
        
        # Get recent posts for the sidebar
        context['recent_posts'] = BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).order_by('-published_date')[:5]
        
        # Get popular posts (most viewed)
        context['popular_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-view_count')[:3]
        
        # Add search query to context
        context['search_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Increment view count
        post.increment_view_count()
        
        # Get related posts (same category)
        context['related_posts'] = BlogPost.objects.filter(
            category=post.category,
            status='published',
            published_date__lte=timezone.now()
        ).exclude(id=post.id)[:3]
        
        # Get comments for this post
        context['comments'] = post.comments.filter(active=True).order_by('created_at')
        
        # Initialize comment form with post ID
        context['comment_form'] = CommentForm(initial={'post': post.id})
        
        # Add recent posts for sidebar
        context['recent_posts'] = BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).exclude(id=post.id).order_by('-published_date')[:5]
        
        # Add categories for sidebar
        context['categories'] = BlogPost.objects.filter(
            status='published'
        ).values_list('category', flat=True).distinct()
        
        # Add tags for the post
        context['tags'] = post.get_tags()
        
        return context
    
    # Comment submission is handled by the add_comment_to_post function view


class BlogPostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    fields = ['title', 'category', 'content', 'excerpt', 'featured_image', 'tags', 'status']
    template_name = 'blog_post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Blog post created successfully!')
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('core:blog_detail', kwargs={'slug': self.object.slug})
    fields = ['title', 'category', 'content', 'excerpt', 'featured_image', 'tags', 'status']
    template_name = 'blog_post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        if not form.instance.excerpt:
            form.instance.excerpt = form.cleaned_data['content'][:200] + '...'
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Your post has been created!')
        return reverse_lazy('core:blog_detail', kwargs={'slug': self.object.slug})


class BlogPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    fields = ['title', 'category', 'content', 'excerpt', 'featured_image', 'tags', 'status']
    template_name = 'blog_post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)
        
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
        
    def get_success_url(self):
        messages.success(self.request, 'Your post has been updated!')
        return reverse_lazy('core:blog_detail', kwargs={'slug': self.object.slug})


class BlogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    template_name = 'blog_post_confirm_delete.html'
    success_url = reverse_lazy('core:blog')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
        
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


def add_comment_to_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.active = True  # Set to False if you want to moderate comments
            comment.save()
            messages.success(request, 'Your comment has been submitted and is awaiting moderation.')
            return redirect('core:blog_detail', slug=post.slug)
    else:
        form = CommentForm(initial={'post': post.id})
    
    # If we get here, the form was invalid or it's a GET request
    context = {
        'post': post,
        'comment_form': form,
        'comments': post.comments.filter(active=True).order_by('created_at'),
        'recent_posts': BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).exclude(id=post.id).order_by('-published_date')[:5],
        'categories': BlogPost.objects.filter(
            status='published'
        ).values_list('category', flat=True).distinct(),
        'tags': post.get_tags()
    }
    return render(request, 'blog_detail.html', context)
