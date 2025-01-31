import locale
import sublime
import sublime_plugin

STATUS_ID  = 'tinycount'
SIZE_LIMIT = 4194304

IGNORE_COMMENTS = True

def plugin_unloaded():
	for window in sublime.windows():
		for view in window.views():
			view.erase_status(STATUS_ID)

class Counter(sublime_plugin.EventListener):
	def __init__(self):
		# we do this to allow thousands separators
		# to be generated according to the user's locale
		locale.setlocale(locale.LC_ALL, '')

		self.is_active          = False
		self.has_selection      = False
		self.just_had_selection = False

	def do_word_count(self, view):
		view_size = view.size()

		if view_size > SIZE_LIMIT:
			view.set_status(STATUS_ID, "[!] Words")
			return

		word_count = 0

		if self.has_selection:
			for selection in view.sel():
				if len(selection) > 0:
					region = sublime.Region(selection.begin(), selection.end())
					word_count += len(view.substr(region).split())

		else:
			word_count += len(view.substr(sublime.Region(0, view_size)).split())

			if IGNORE_COMMENTS:
				comment_count = 0
				for region in view.find_by_selector("comment"):
					comment_count += len(view.substr(region).split())

				word_count -= comment_count

		view.set_status(STATUS_ID, '{:n} Words'.format(word_count))

	def on_activated_async(self, view):
		self.is_active = view.window().is_status_bar_visible() and "text." in view.scope_name(0)

		if not self.is_active:
			# we're not unloading the plugin,
			# we're just calling the sublime
			# callback ourselves because it
			# does everything we need for this
			# step. might not always be true!
			plugin_unloaded()
			return

		self.do_word_count(view)

	def on_post_save_async(self, view):
		if not self.is_active:
			return

		self.do_word_count(view)

	def on_reload_async(self, view):
		if not self.is_active:
			return

		self.do_word_count(view)

	# maddeningly moving the caret without an active region selection
	# also fires this, so we do some extra work to reduce expenditure
	def on_selection_modified_async(self, view):
		if not self.is_active:
			return

		selection_total = 0
		for selection in view.sel():
			selection_total += len(selection)

		self.has_selection = selection_total > 0

		if self.has_selection:
			self.just_had_selection = True
			self.do_word_count(view)

		# this ensures a single reset when all
		# selections are cleared, otherwise
		# you're left with the last known
		# selection until a save or view change
		elif self.just_had_selection:
			self.do_word_count(view)
			self.just_had_selection = False
