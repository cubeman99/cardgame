#ifndef _ENUMS_H_
#define _ENUMS_H_

#include <string>
#include <map>


namespace enums {

{enums_begin}
enum class {enum_name}
{
{items_begin}	{item_name}{name_padding} = {item_value},
{items_end}};
{enums_end}

template <typename T_Enum>
class EnumMap
{
public:
	static const std::string ENUM_NAME;
	static const std::map<T_Enum, std::string> VALUE_TO_STRING;
	static const std::map<std::string, T_Enum> STRING_TO_VALUE;
	static const std::map<std::string, int> STRING_TO_INT;
};

template <typename T_Enum>
const std::string EnumMap<T_Enum>::ENUM_NAME = "UNKNOWN";
template <typename T_Enum>
const std::map<T_Enum, std::string> EnumMap<T_Enum>::VALUE_TO_STRING = {};
template <typename T_Enum>
const std::map<std::string, T_Enum> EnumMap<T_Enum>::STRING_TO_VALUE = {};
template <typename T_Enum>
const std::map<std::string, int> EnumMap<T_Enum>::STRING_TO_INT = {};


// Convert an enum value to a string name.
template <typename T_Enum>
T_Enum ParseValue(std::string name)
{
	// Convert name to uppercase first
	std::transform(name.begin(), name.end(), name.begin(), ::toupper);
	return EnumMap<T_Enum>::STRING_TO_VALUE.at(name);
}

// Convert an string name to an enum value.
template <typename T_Enum>
std::string ValueName(T_Enum value)
{
	return EnumMap<T_Enum>::VALUE_TO_STRING.at(value);
}

// Return the string representation of an enum's name.
template <typename T_Enum>
std::string EnumName();

// Return the type of a tag.
Type GetTagType(GameTag tag);

std::string GetTagEnumValueName(GameTag tag, int value);


{enums_begin}
template <> class EnumMap<{enum_name}>
{
public:
	static const std::string ENUM_NAME;
	static const std::map<{enum_name}, std::string> VALUE_TO_STRING;
	static const std::map<std::string, {enum_name}> STRING_TO_VALUE;
	static const std::map<std::string, int> STRING_TO_INT;
};
{enums_end}

class TypeInfoBase
{
public:
	virtual int NameToInt(std::string name) const = 0;
	virtual std::string IntToName(int value) const = 0;
	virtual const std::string& GetEnumName() const = 0;
};

template <typename T_Enum>
class TypeInfo : public TypeInfoBase
{
public:
	TypeInfo(int x):
	{}
	TypeInfo(const std::string& name,
			std::map<std::string, int> nameToValue,
			std::map<int, std::string> valueToName) :
		m_enumName(name),
		m_nameToValue(nameToValue),
		m_valueToName(valueToName)
	{
	}

	const std::string& GetEnumName() const override
	{
		return m_enumName;
	}

	int NameToInt(std::string name) const override
	{
		std::transform(name.begin(), name.end(), name.begin(), ::toupper);
		return m_nameToValue.at(name);
	}

	std::string IntToName(int value) const override
	{
		return m_valueToName.at(value);
	}

	T_Enum NameToValue(std::string name) const
	{
		return (T_Enum) NameToInt(name);
	}

	std::string ValueToName(T_Enum value) const
	{
		return IntToName((int) value);
	}

private:
	std::string m_enumName;
	std::map<std::string, int> m_nameToValue;
	std::map<int, std::string> m_valueToName;
};

const TypeInfoBase* GetTagTypeInfo(GameTag tag);


}; // namespace enums

#endif // _ENUMS_H_