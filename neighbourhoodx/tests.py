from django.test import TestCase
from django.contrib.auth.models import User
from .models import Administrator, Neighbourhood, Member, Business, SocialServices, Post

# test template
# Create your tests here.
class AdministratorTestClass(TestCase):
    def setUp(self):
        self.new_obj = User(username = "new_obj", email = "new_obj@gmail.com",password = "pass")
        self.Administrator = Administrator(bio='bio', user= self.new_obj)
        self.new_obj.save()

    def tearDown(self):
        Administrator.objects.all().delete()
        User.objects.all().delete()

    def test_instance(self):
        self.assertTrue(isinstance(self.new_obj, User))
        self.assertTrue(isinstance(self.Administrator, Administrator))


class NeighbourhoodTestClass(TestCase):
    def setUp(self):
        self.new_obj = User(username = "new_obj", email = "new_obj@gmail.com",password = "pass")
        self.Administrator = Administrator(bio='bio', user= self.new_obj)

        self.project = Neighbourhood(image = 'imageurl', name ='img', description = 'img-cap', Administrator = self.Administrator)
        
        self.new_obj.save()
        self.Administrator.save()
        self.project.save()

    def tearDown(self):
        Administrator.objects.all().delete()
        User.objects.all().delete()

    def test_instance(self):
        self.assertTrue(isinstance(self.img, Neighbourhood))

    def test_save(self):
        Neighbourhoods = Neighbourhood.objects.all()
        self.assertTrue(len(projects)> 0)

    def test_delete(self):
        Neighbourhoods = Neighbourhood.objects.all()
        self.assertEqual(len(projects),1)
        self.project.delete()
        new_list = Neighbourhood.objects.all()
        self.assertEqual(len(new_list),0)

class BusinessTestClass(TestCase):
    def setUp(self):
        self.new_obj = User(username = "new_obj", email = "new_obj@gmail.com",password = "pass")
        self.Administrator = Administrator(bio='bio', user= self.new_obj)

        self.two = User(username = "two", email = "two@gmail.com",password = "pass")
        self.Administrator2 = Administrator(bio='bio', user= self.two) 

        self.new.save()
        self.two.save()

        self.Business = Business (whoIsBusinessing = self.Administrator, WhoToBusiness = self.two )
        
    def tearDown(self):
        Administrator.objects.all().delete()        
        User.objects.all().delete()
        
    def test_instance(self):
        self.assertTrue(isinstance(self.Business,Business))

class MemberTestClass(TestCase):
    def setUp(self):
        self.new_obj = User(username = "new_obj", email = "new_obj@gmail.com",password = "pass")
        self.Administrator = Administrator(bio='bio', user= self.new_obj)

        self.project = Neighbourhood(image = 'imageurl', name ='img', description = 'img-cap', Administrator = self.Administrator)

        self.Member = Member(user=self.new_obj, Neighbourhood=self.project, design= 10,  usability= 10, content = 10, creativity = 10, average = 10)
        self.new_obj.save()
        self.Administrator.save()
        self.project.save()
        self.Member.save()

    def tearDown(self):
        Administrator.objects.all().delete()
        User.objects.all().delete()
        Member.objects.all().delete()

    def test_instance(self):
        self.assertTrue(isinstance(self.Member, Member))

    def test_save(self):
        Members = Member.objects.all()
        self.assertTrue(len(Members)> 0)

    def test_delete(self):
        Members = Neighbourhood.objects.all()
        self.assertEqual(len(Members),1)
        self.Member.delete()
        new_list = Member.objects.all()
        self.assertEqual(len(new_list),0)

class SocialServicesTestClass(TestCase):
    def setUp(self):
        self.new = SocialServices(bio='bio', user= self.new_obj)
    pass

class PostTestClass(TestCase):
    def setUp(self):
        self.new = Post(bio='bio', user= self.new_obj)
    pass