from abc import ABC, abstractmethod

# 抽象基底クラス
class Animal(ABC):
    # sound()が抽象メソッドであることを宣言
    @abstractmethod
    def sound(self) -> str:
        # 抽象メソッドには具体的な実装は書かない
        pass

class Dog(Animal):
    # Animalを継承し、soundが実装されている
    def sound(self) -> str:
        return "Bow-wow"

# プロトコルを無視しているのでエラーが出る例
class Book(Animal): # Animalを継承
    # Animalを継承したが、soundが実装されていない
    def read(self) -> str:
        return "hogeeee"

# プロトコルを無視しているので静的解析でエラーが出る例
class Cat(Animal):
    # Animalを継承し、soundは実装されているが、戻り値が違う
    # 抽象クラスの要求(-> str)とは異なる戻り値(-> None)
    def sound(self) -> None: 
        print("Meow")
        
        
dog = Dog()
dog_sound = dog.sound()
print(dog_sound)

# book = Book()
# book.sound()

cat = Cat()
cat.sound()

